"""Bootstrap utilities for application initialization.

Provides a way to bootstrap the application components including
the observability manager and the message bus, plus standardized
Python logging (console + rotating file).
"""

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Callable, Generic, Optional, Type, TypeVar

from dotenv import load_dotenv

from llmgine.bus.bus import MessageBus
from llmgine.bus.session import BusSession
from llmgine.messages.commands import Command
from llmgine.messages.events import Event
from llmgine.observability.events import LogLevel
from llmgine.observability.handlers.adapters import (
    create_sync_console_handler,
    create_sync_file_handler,
)
from llmgine.observability.manager import ObservabilityManager

load_dotenv(override=True)

logger = logging.getLogger(__name__)

# Type definitions
TConfig = TypeVar("TConfig")

_DEFAULT_LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s | session=%(session_id)s"
)

class _SessionContextFilter(logging.Filter):
    """Ensures 'session_id' is always present in log records, so formatters never break.
    Developers can pass extra={'session_id': '<id>'} to override per record."""
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "session_id"):
            record.session_id = "-"
        return True


# --- Basic Logging Setup Function ---
def setup_basic_logging(
    *,
    level: LogLevel = LogLevel.INFO,
    enable_console: bool = True,
    enable_file: bool = False,
    file_dir: str = "logs",
    file_name: Optional[str] = None,
    fmt: Optional[str] = None,
) -> None:
    """Configure standard Python logging (console + rotating file).

    Args:
        level: Base log level (can be overridden by $LLMGINE_LOG_LEVEL).
        enable_console: If True, attach a StreamHandler.
        enable_file: If True, attach a RotatingFileHandler.
        file_dir: Directory for the log file.
        file_name: Optional explicit file name; otherwise timestamped.
        fmt: Optional log format. Defaults to a useful, compact format with session id.
    """
    log_level_map = {
        LogLevel.DEBUG: logging.DEBUG,
        LogLevel.INFO: logging.INFO,
        LogLevel.WARNING: logging.WARNING,
        LogLevel.ERROR: logging.ERROR,
        LogLevel.CRITICAL: logging.CRITICAL,
    }
    # Env override for convenience
    env_level = (os.getenv("LLMGINE_LOG_LEVEL") or "").strip().upper()
    if env_level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        target_level = getattr(logging, env_level, logging.INFO)
    else:
        target_level = log_level_map.get(level, logging.INFO)

    root = logging.getLogger()
    root.setLevel(target_level)

    formatter = logging.Formatter(fmt or _DEFAULT_LOG_FORMAT)
    session_filter = _SessionContextFilter()

    # Avoid duplicate handlers when called multiple times
    existing_types = {type(h).__name__ for h in root.handlers}

    if enable_console and "StreamHandler" not in existing_types:
        sh = logging.StreamHandler()
        sh.setFormatter(formatter)
        sh.addFilter(session_filter)
        root.addHandler(sh)

    if enable_file and "RotatingFileHandler" not in existing_types:
        os.makedirs(file_dir, exist_ok=True)
        fname = file_name or f"app_{datetime.now():%Y%m%d_%H%M%S}.log"
        fh = RotatingFileHandler(
            os.path.join(file_dir, fname), maxBytes=10_000_000, backupCount=5
        )
        fh.setFormatter(formatter)
        fh.addFilter(session_filter)
        root.addHandler(fh)

    logger.info("Basic logging configured", extra={"session_id": "-"})


@dataclass
class ApplicationConfig:
    """Base configuration for applications."""

    # General application config
    name: str = "application"
    description: str = "application description"

    # --- Standard Logging Config ---
    # Controls standard Python logging setup (not MessageBus handlers)
    log_level: LogLevel = LogLevel.INFO
    pylog_enable_console: bool = True
    pylog_enable_file: bool = False
    pylog_file_dir: str = "logs"
    pylog_file_name: Optional[str] = None
    pylog_format: str = _DEFAULT_LOG_FORMAT

    # --- Observability Handler Config ---
    enable_console_handler: bool = True
    enable_file_handler: bool = True
    file_handler_log_dir: str = "logs"
    file_handler_log_filename: Optional[str] = None  # Default: timestamped events.jsonl
    # custom_handlers: List[ObservabilityEventHandler] = field(default_factory=list) # For adding other handlers


class ApplicationBootstrap(Generic[TConfig]):
    """Bootstrap for application initialization.

    Handles setting up the message bus and registering configured
    observability event handlers.
    """

    def __init__(self, config: Optional[TConfig] = None):
        """Initialize the bootstrap.

        Args:
            config: Application configuration
        """
        self.config = config if config is not None else ApplicationConfig()

        # --- Configure Standard Logging ---
        setup_basic_logging(
            level=getattr(self.config, "log_level", LogLevel.INFO),
            enable_console=getattr(self.config, "pylog_enable_console", True),
            enable_file=getattr(self.config, "pylog_enable_file", False),
            file_dir=getattr(self.config, "pylog_file_dir", "logs"),
            file_name=getattr(self.config, "pylog_file_name", None),
            fmt=getattr(self.config, "pylog_format", _DEFAULT_LOG_FORMAT),
        )
        # --- End Logging Config ---

        # --- Initialize ObservabilityManager ---
        self.observability = ObservabilityManager()

        # --- Initialize MessageBus with ObservabilityManager ---
        self.message_bus = MessageBus(observability=self.observability)

    async def bootstrap(self) -> None:
        """Bootstrap the application.

        Starts the message bus, and registers handlers.
        """
        logger.info(
            "Application bootstrap started", extra={"component": "ApplicationBootstrap"}
        )

        # Start message bus
        await self.message_bus.start()

        # Create a primary session so apps can register handlers without
        # needing to manage a session explicitly.
        # (This matches shutdown() which already cleans it up.)
        self.primary_session = self.create_session()
        await self.primary_session.start()

        # Register command and event handlers
        self._register_observability_handlers()
        self._register_command_handlers()
        self._register_event_handlers()

        logger.info(
            "Application bootstrap completed", extra={"component": "ApplicationBootstrap"}
        )

    async def shutdown(self) -> None:
        """Shutdown the application components."""
        # Close the primary session (using __aexit__ since it's an async context manager)
        if hasattr(self, "primary_session") and self.primary_session._active:
            await self.primary_session.__aexit__(None, None, None)

        # Stop message bus
        await self.message_bus.stop()

        logger.info(
            "Application shutdown complete", extra={"component": "ApplicationBootstrap"}
        )

    def _register_observability_handlers(self) -> None:
        """Register observability handlers with the ObservabilityManager."""
        if self.config.enable_console_handler:
            self.observability.register_handler(create_sync_console_handler())
        if self.config.enable_file_handler:
            log_dir = getattr(self.config, "file_handler_log_dir", "logs")
            filename = getattr(self.config, "file_handler_log_filename", None)
            self.observability.register_handler(
                create_sync_file_handler(log_dir=log_dir, filename=filename)
            )

    def _register_command_handlers(self) -> None:
        """Register command handlers with the message bus.

        Override this method to register your engine's command handlers.
        """
        pass

    def _register_event_handlers(self) -> None:
        """Register event handlers with the message bus.

        Override this method to register your engine's event handlers.
        """
        pass

    def register_command_handler(
        self, command_type: Type[Command], handler: Callable
    ) -> None:
        """Register a command handler with the message bus.

        Args:
            command_type: The type of command to handle
            handler: The function that handles the command
        """
        # Use the primary session as the default
        self.primary_session.register_command_handler(command_type, handler)

    def register_event_handler(self, event_type: Type[Event], handler: Callable) -> None:
        """Register an event handler with the message bus.

        Args:
            event_type: The type of event to handle
            handler: The function that handles the event
        """
        # Use the primary session as the default
        self.primary_session.register_event_handler(event_type, handler)

    def create_session(self) -> BusSession:
        """Create a new session for session-specific handlers.

        Returns:
            A new BusSession that can be used as a context manager
        """
        return self.message_bus.create_session()


class CommandBootstrap(ApplicationBootstrap[TConfig]):
    """Legacy bootstrap class for backward compatibility."""

    pass
