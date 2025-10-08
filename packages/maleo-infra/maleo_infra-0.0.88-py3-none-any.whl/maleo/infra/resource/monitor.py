import asyncio
import os
import psutil
import traceback
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID, uuid4
from maleo.logging.enums import Level
from maleo.logging.logger import EnvironmentT, ServiceKeyT, Application
from maleo.schemas.application import ApplicationContext, OptionalApplicationContext
from maleo.schemas.connection import OptionalConnectionContext
from maleo.schemas.operation.action.system import SystemOperationAction
from maleo.schemas.operation.context import generate
from maleo.schemas.operation.enums import (
    SystemOperationType,
    Origin,
    Layer,
    Target,
)
from maleo.schemas.operation.mixins import Timestamp
from maleo.schemas.operation.system import SuccessfulSystemOperation
from maleo.schemas.pagination import FlexiblePagination
from maleo.schemas.response import (
    SingleDataResponse,
    MultipleDataResponse,
)
from maleo.schemas.security.authentication import OptionalAnyAuthentication
from maleo.schemas.security.authorization import OptionalAnyAuthorization
from maleo.schemas.security.impersonation import OptionalImpersonation
from maleo.types.uuid import OptionalUUID
from .config import Config
from .constants import STATUS_LOG_LEVEL
from .schemas import CPUUsage, MemoryUsage, Usage, AggregateUsage, Measurement
from .utils import aggregate_status


class ResourceMonitor:
    def __init__(
        self,
        config: Config,
        logger: Application[EnvironmentT, ServiceKeyT],
        application_context: OptionalApplicationContext = None,
    ):
        self.application_context = (
            application_context
            if application_context is not None
            else ApplicationContext.from_env()
        )
        self.config = config
        self.logger = logger
        self.process = psutil.Process(os.getpid())
        self.cpu_window = deque(maxlen=self.config.measurement.window)

        # Store historical data with timestamps
        self.measurement_history: deque[Measurement[Usage]] = deque(
            maxlen=10_000
        )  # Adjust max length as needed
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

        # Operation context setup
        self.operation_context = generate(
            origin=Origin.SERVICE, layer=Layer.INFRASTRUCTURE, target=Target.MONITORING
        )
        self.operation_action = SystemOperationAction(
            type=SystemOperationType.METRIC_REPORT, details={"type": "resource"}
        )

    async def start_monitoring(
        self,
        operation_id: OptionalUUID = None,
    ) -> None:
        """Start the resource monitoring loop."""
        operation_id = operation_id if operation_id is not None else uuid4()
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop(operation_id))

    async def stop_monitoring(self) -> None:
        """Stop the resource monitoring loop."""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None

    async def _monitor_loop(
        self,
        operation_id: UUID,
    ) -> None:
        """Internal monitoring loop."""
        count: int = 1
        while self.is_monitoring:
            try:
                await self._measure(
                    operation_id, self.config.measurement.frequency == count
                )
                if count >= self.config.measurement.frequency:
                    count = 1
                else:
                    count += 1
                await asyncio.sleep(self.config.measurement.interval)
            except asyncio.CancelledError:
                break
            except Exception:
                print("Error in resource monitoring:")
                print(traceback.format_exc())
                await asyncio.sleep(self.config.measurement.interval)

    def _cleanup_old_entries(self) -> None:
        """Remove entries older than max_age_seconds (default: 1 hour)."""
        if not self.measurement_history:
            return

        cutoff_time = datetime.now(tz=timezone.utc) - timedelta(
            seconds=self.config.retention
        )

        # Remove old entries from the left
        while (
            self.measurement_history
            and self.measurement_history[0].measured_at < cutoff_time
        ):
            self.measurement_history.popleft()

    async def _measure(
        self, operation_id: UUID, log: bool = True
    ) -> SingleDataResponse[Measurement[Usage], None]:
        """Collect current resource usage and store in history."""
        executed_at = datetime.now(tz=timezone.utc)

        # Raw CPU usage since last call
        raw_cpu = self.process.cpu_percent(interval=None)

        # Update moving window for smoothing
        self.cpu_window.append(raw_cpu)
        smooth_cpu = sum(self.cpu_window) / len(self.cpu_window)

        # Memory usage in MB
        raw_memory = self.process.memory_info().rss / (1024 * 1024)

        timestamp = Timestamp.completed_now(executed_at)

        cpu_usage = CPUUsage.new(
            raw=raw_cpu, smooth=smooth_cpu, config=self.config.usage.cpu
        )
        memory_usage = MemoryUsage.new(raw=raw_memory, config=self.config.usage.memory)
        usage = Usage(cpu=cpu_usage, memory=memory_usage)
        status = aggregate_status(
            usage.cpu.status,
            usage.memory.status,
        )
        measurement = Measurement[Usage](
            measured_at=timestamp.completed_at,
            status=status,
            usage=usage,
        )

        # Store in history with timestamp
        self.measurement_history.append(measurement)

        # Clean up old entries (older than max retention period)
        self._cleanup_old_entries()

        response = SingleDataResponse[Measurement[Usage], None](
            data=measurement, metadata=None, other=None
        )

        if log:
            SuccessfulSystemOperation[SingleDataResponse[Measurement[Usage], None]](
                application_context=self.application_context,
                id=operation_id,
                context=self.operation_context,
                action=self.operation_action,
                timestamp=timestamp,
                summary=(
                    f"Successfully measured resource usage - {status}"
                    f" - CPU | Status: {cpu_usage.status} | Raw: {cpu_usage.raw:.2f}% | Smooth: {cpu_usage.smooth:.2f}%"
                    f" - Memory | Status {memory_usage.status} | Raw: {memory_usage.raw:.2f}MB | Percentage: {memory_usage.percentage:.2f}%"
                ),
                connection_context=None,
                authentication=None,
                authorization=None,
                impersonation=None,
                response=response,
            ).log(self.logger, STATUS_LOG_LEVEL[status])

        return response

    def get_last_measurement(
        self,
        *,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> Optional[SingleDataResponse[Measurement[Usage], None]]:
        """Get the most recent resource usage data."""
        if not self.measurement_history:
            return None

        data = self.measurement_history[-1]
        response = SingleDataResponse[Measurement[Usage], None](
            data=data, metadata=None, other=None
        )

        SuccessfulSystemOperation[SingleDataResponse[Measurement[Usage], None],](
            application_context=self.application_context,
            id=operation_id if operation_id is not None else uuid4(),
            context=self.operation_context,
            action=self.operation_action,
            timestamp=Timestamp.now(),
            summary="Successfully retrieved last resource usage measurement",
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
            response=response,
        ).log(self.logger, Level.INFO)

        return response

    def clear_history(self) -> None:
        """Clear all stored resource usage history."""
        self.measurement_history.clear()

    def count_history(self) -> int:
        """Get the number of entries in history."""
        return len(self.measurement_history)

    def get_measurement_history(
        self,
        window: int = 60,
        *,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> MultipleDataResponse[Measurement[Usage], FlexiblePagination, None]:
        """
        Get resource usage data from the last X seconds.

        Args:
            window: Number of seconds to look back

        Returns:
            List of dicts with 'timestamp' and 'resource_usage' keys
        """
        operation_id = operation_id if operation_id is not None else uuid4()
        executed_at = datetime.now(tz=timezone.utc)

        if not self.measurement_history:
            data = []
        else:
            cutoff_time = executed_at - timedelta(seconds=window)
            data = [
                entry
                for entry in self.measurement_history
                if entry.measured_at >= cutoff_time
            ]

        timestamp = Timestamp.completed_now(executed_at)

        pagination = FlexiblePagination(
            page=1,
            limit=None,
            data_count=len(data),
            total_data=len(data),
            total_pages=1,
        )

        response = MultipleDataResponse[Measurement[Usage], FlexiblePagination, None](
            data=data, pagination=pagination, metadata=None, other=None
        )

        SuccessfulSystemOperation[
            MultipleDataResponse[Measurement[Usage], FlexiblePagination, None],
        ](
            application_context=self.application_context,
            id=operation_id,
            context=self.operation_context,
            action=self.operation_action,
            timestamp=timestamp,
            summary=f"Retrieved {len(data)} resource measurement entries from the last {window} seconds",
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
            response=response,
        ).log(
            self.logger, Level.INFO
        )

        return response

    def get_average_usage(
        self,
        window: int = 60,
        *,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> Optional[SingleDataResponse[Measurement[AggregateUsage], None]]:
        """
        Calculate average resource usage over the last X seconds.

        Args:
            window: Number of seconds to look back

        Returns:
            Measurement with averaged values, or None if no data
        """
        operation_id = operation_id if operation_id is not None else uuid4()
        executed_at = datetime.now(tz=timezone.utc)

        history_response = self.get_measurement_history(
            window,
            operation_id=operation_id,
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
        )
        history_data = history_response.data
        if not history_data:
            return None

        measured_at = datetime.now(tz=timezone.utc)

        # Calculate averages
        total_raw_cpu = sum(entry.usage.cpu.raw for entry in history_data)
        total_smooth_cpu = sum(entry.usage.cpu.smooth for entry in history_data)
        total_memory = sum(entry.usage.memory.raw for entry in history_data)
        count = len(history_data)

        avg_cpu = CPUUsage.new(
            raw=total_raw_cpu / count,
            smooth=total_smooth_cpu / count,
            config=self.config.usage.cpu,
        )

        avg_memory = MemoryUsage.new(
            raw=total_memory / count, config=self.config.usage.memory
        )

        status = aggregate_status(
            avg_cpu.status,
            avg_memory.status,
        )

        timestamp = Timestamp.completed_now(executed_at)

        data = Measurement[AggregateUsage](
            measured_at=measured_at,
            status=status,
            usage=AggregateUsage(cpu=avg_cpu, memory=avg_memory, window=window),
        )

        response = SingleDataResponse[Measurement[AggregateUsage], None](
            data=data, metadata=None, other=None
        )

        SuccessfulSystemOperation[
            SingleDataResponse[Measurement[AggregateUsage], None],
        ](
            application_context=self.application_context,
            id=operation_id,
            context=self.operation_context,
            action=self.operation_action,
            timestamp=timestamp,
            summary=(
                f"Successfully measured average resource usage of the last {window} seconds - {status}"
                f" - CPU | Status: {avg_cpu.status} | Raw: {avg_cpu.raw:.2f}% | Smooth: {avg_cpu.smooth:.2f}%"
                f" - Memory | Status: {avg_memory.status} | Raw: {avg_memory.raw:.2f}MB | Percentage: {avg_memory.percentage:.2f}%"
            ),
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
            response=response,
        ).log(
            self.logger, Level.INFO
        )

        return response

    def get_peak_usage(
        self,
        window: int = 60,
        *,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> Optional[SingleDataResponse[Measurement[AggregateUsage], None]]:
        """
        Get peak resource usage over the last X seconds.

        Args:
            seconds: Number of seconds to look back

        Returns:
            Measurement with peak values, or None if no data
        """
        operation_id = operation_id if operation_id is not None else uuid4()
        executed_at = datetime.now(tz=timezone.utc)

        history_response = self.get_measurement_history(
            window,
            operation_id=operation_id,
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
        )
        history_data = history_response.data
        if not history_data:
            return None

        measured_at = datetime.now(tz=timezone.utc)

        # Find peaks
        peak_raw_cpu = max(entry.usage.cpu.raw for entry in history_data)
        peak_smooth_cpu = max(entry.usage.cpu.smooth for entry in history_data)
        peak_raw_memory = max(entry.usage.memory.raw for entry in history_data)

        peak_cpu = CPUUsage.new(
            raw=peak_raw_cpu, smooth=peak_smooth_cpu, config=self.config.usage.cpu
        )

        peak_memory = MemoryUsage.new(
            raw=peak_raw_memory, config=self.config.usage.memory
        )

        status = aggregate_status(
            peak_cpu.status,
            peak_memory.status,
        )

        timestamp = Timestamp.completed_now(executed_at)

        data = Measurement[AggregateUsage](
            measured_at=measured_at,
            status=status,
            usage=AggregateUsage(cpu=peak_cpu, memory=peak_memory, window=window),
        )

        response = SingleDataResponse[Measurement[AggregateUsage], None](
            data=data, metadata=None, other=None
        )

        SuccessfulSystemOperation[
            SingleDataResponse[Measurement[AggregateUsage], None],
        ](
            application_context=self.application_context,
            id=operation_id,
            context=self.operation_context,
            action=self.operation_action,
            timestamp=timestamp,
            summary=(
                f"Successfully measured peak resource usage of the last {window} seconds - {status}"
                f" - CPU | Status: {peak_cpu.status} | Raw: {peak_cpu.raw:.2f}% | Smooth: {peak_cpu.smooth:.2f}%"
                f" - Memory | Status: {peak_memory.status} | Raw: {peak_memory.raw:.2f}MB | Percentage: {peak_memory.percentage:.2f}%"
            ),
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
            response=response,
        ).log(
            self.logger, Level.INFO
        )

        return response

    async def get_instant_usage(
        self,
        *,
        operation_id: OptionalUUID = None,
        connection_context: OptionalConnectionContext = None,
        authentication: OptionalAnyAuthentication = None,
        authorization: OptionalAnyAuthorization = None,
        impersonation: OptionalImpersonation = None,
    ) -> SingleDataResponse[Measurement[Usage], None]:
        """
        Get an instant resource usage reading without affecting the monitoring loop.
        This doesn't store the result in history.
        """
        operation_id = operation_id if operation_id is not None else uuid4()
        executed_at = datetime.now(tz=timezone.utc)

        raw_cpu = self.process.cpu_percent(interval=None)
        raw_memory = self.process.memory_info().rss / (1024 * 1024)

        # For instant reading, use the current smooth CPU from the window
        # or raw CPU if no history exists
        smooth_cpu = (
            sum(self.cpu_window) / len(self.cpu_window) if self.cpu_window else raw_cpu
        )

        measured_at = datetime.now(tz=timezone.utc)

        cpu_usage = CPUUsage.new(
            raw=raw_cpu, smooth=smooth_cpu, config=self.config.usage.cpu
        )
        memory_usage = MemoryUsage.new(raw=raw_memory, config=self.config.usage.memory)

        usage = Usage(cpu=cpu_usage, memory=memory_usage)
        status = aggregate_status(
            usage.cpu.status,
            usage.memory.status,
        )

        timestamp = Timestamp.completed_now(executed_at)

        data = Measurement(measured_at=measured_at, status=status, usage=usage)

        response = SingleDataResponse[Measurement[Usage], None](
            data=data, metadata=None, other=None
        )

        SuccessfulSystemOperation[SingleDataResponse[Measurement[Usage], None],](
            application_context=self.application_context,
            id=operation_id,
            context=self.operation_context,
            action=self.operation_action,
            timestamp=timestamp,
            summary=(
                f"Successfully measured instant resource usage - {status}"
                f" - CPU | Status: {cpu_usage.status} | Raw: {cpu_usage.raw:.2f}% | Smooth: {cpu_usage.smooth:.2f}%"
                f" - Memory | Status: {memory_usage.status} | Raw: {memory_usage.raw:.2f}MB | Percentage: {memory_usage.percentage:.2f}%"
            ),
            connection_context=connection_context,
            authentication=authentication,
            authorization=authorization,
            impersonation=impersonation,
            response=response,
        ).log(self.logger, Level.INFO)

        return response

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()
