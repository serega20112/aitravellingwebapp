"""Logging setup module for configuring application logging.

This module provides comprehensive logging configuration including file logging,
Elasticsearch integration, and JSON formatting for structured logs.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from logging.handlers import RotatingFileHandler

from flask import Flask, Response, g, has_request_context, request

from src.backend.infrastructure.logging.es_handler import ElasticsearchHandler


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    This formatter converts log records to JSON format for better
    parsing and analysis in log aggregation systems.

    Attributes:
        pretty: Whether to format JSON with indentation for readability
    """

    def __init__(self, pretty: bool = False) -> None:
        """Initialize JSON formatter.

        Args:
            pretty: If True, format JSON with indentation
        """
        super().__init__()
        self.pretty = pretty

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log message
        """
        data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
        }
        if self.pretty:
            return json.dumps(data, ensure_ascii=False, indent=2)
        return json.dumps(data, ensure_ascii=False)


class RequestContextFilter(logging.Filter):
    """Впрыскивает request_id и user_id (если есть) в записи логов."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Inject request-related fields into the log record.

        Returns True to allow the record to pass through the filter chain.
        """
        # Защита от использования вне контекста приложения/запроса
        if has_request_context():
            record.request_id = getattr(g, "request_id", None)
            record.user_id = getattr(getattr(g, "user", None), "id", None)
        else:
            record.request_id = None
            record.user_id = None
        return True


class ErrorsPerFileHandler(logging.Handler):
    """Пишет только ERROR и выше в отдельные файлы по имени исходного файла.

    Пример пути: logs/errors/<module>.log (с ротацией).
    """

    def __init__(self, base_dir: str, max_bytes: int, backup_count: int) -> None:
        """Initialize handler that writes errors per module into separate files."""
        super().__init__(level=logging.ERROR)
        self.base_dir = base_dir
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._handlers: dict[str, RotatingFileHandler] = {}
        os.makedirs(self.base_dir, exist_ok=True)

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover (IO)
        """Emit a record writing it into a file named after the source module."""
        if record.levelno < logging.ERROR:
            return
        base = os.path.basename(record.pathname) if record.pathname else "errors"
        stem, _ext = os.path.splitext(base)
        target_path = os.path.join(self.base_dir, f"{stem}.log")
        handler = self._handlers.get(target_path)
        if handler is None:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            handler = RotatingFileHandler(
                target_path, maxBytes=self.max_bytes, backupCount=self.backup_count
            )
            # форматтер возьмём из текущего хендлера, если есть
            fmt = getattr(self, "formatter", None)
            if fmt is not None:
                handler.setFormatter(fmt)
            self._handlers[target_path] = handler
        handler.emit(record)


def setup_logging(app: Flask) -> None:
    """Configure logging for the Flask application.

    Sets up console, file, per-file error logging and optional Elasticsearch
    logging. Also installs request hooks for assigning request IDs and writing
    access logs.
    """
    cfg = app.config

    log_level = getattr(
        logging, str(cfg.get("LOG_LEVEL", "INFO")).upper(), logging.INFO
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Очищаем существующие хендлеры, чтобы не дублировать
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    formatter = JsonFormatter(pretty=bool(cfg.get("LOG_PRETTY_JSON", True)))
    context_filter = RequestContextFilter()

    # Console
    if cfg.get("LOG_TO_CONSOLE", True):
        ch = logging.StreamHandler()
        ch.setLevel(
            getattr(
                logging,
                str(cfg.get("LOG_CONSOLE_LEVEL", cfg.get("LOG_LEVEL", "INFO"))).upper(),
                log_level,
            )
        )
        ch.setFormatter(formatter)
        ch.addFilter(context_filter)
        root_logger.addHandler(ch)

    # File rotating
    if cfg.get("LOG_TO_FILE", True):
        log_file = cfg.get("LOG_FILE", "logs/app.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        fh = RotatingFileHandler(
            log_file,
            maxBytes=int(cfg.get("LOG_MAX_BYTES", 10 * 1024 * 1024)),
            backupCount=int(cfg.get("LOG_BACKUP_COUNT", 5)),
        )
        fh.setLevel(
            getattr(
                logging,
                str(cfg.get("LOG_FILE_LEVEL", cfg.get("LOG_LEVEL", "INFO"))).upper(),
                log_level,
            )
        )
        fh.setFormatter(formatter)
        fh.addFilter(context_filter)
        root_logger.addHandler(fh)

    # Errors per file
    if cfg.get("LOG_ERRORS_PER_FILE", True):
        eph = ErrorsPerFileHandler(
            base_dir=cfg.get("LOG_ERRORS_DIR", "logs/errors"),
            max_bytes=int(cfg.get("LOG_MAX_BYTES", 10 * 1024 * 1024)),
            backup_count=int(cfg.get("LOG_BACKUP_COUNT", 5)),
        )
        eph.setLevel(logging.ERROR)
        eph.setFormatter(formatter)
        eph.addFilter(context_filter)
        root_logger.addHandler(eph)

    # Elasticsearch
    if cfg.get("LOG_TO_ES", False):
        es_host = cfg.get("ELASTICSEARCH_HOST")
        if not es_host:
            logging.getLogger(__name__).warning(
                (
                    "LOG_TO_ES=true, но ELASTICSEARCH_HOST не задан — "
                    "отправка логов в ES отключена"
                )
            )
            esh = None
        else:
            esh = ElasticsearchHandler(
                es_host=cfg.get("ELASTICSEARCH_HOST"),
                index_name=cfg.get("ES_INDEX_NAME", "logs-app"),
                username=cfg.get("ES_USERNAME"),
                password=cfg.get("ES_PASSWORD"),
                verify_certs=bool(cfg.get("ES_VERIFY_CERTS", False)),
                ca_certs=cfg.get("ES_CA_CERTS"),
                request_timeout=int(cfg.get("ES_REQUEST_TIMEOUT", 5)),
                level=getattr(
                    logging,
                    str(cfg.get("LOG_ES_LEVEL", "ERROR")).upper(),
                    logging.ERROR,
                ),
            )
        if esh is not None:
            esh.addFilter(context_filter)
            root_logger.addHandler(esh)
            if getattr(esh, "enabled", False):
                logging.getLogger(__name__).info(
                    "Elasticsearch logging ENABLED: host=%s index=%s level=%s",
                    cfg.get("ELASTICSEARCH_HOST"),
                    cfg.get("ES_INDEX_NAME", "logs-app"),
                    getattr(
                        logging,
                        str(cfg.get("LOG_ES_LEVEL", "ERROR")).upper(),
                        logging.ERROR,
                    ),
                )
            else:
                logging.getLogger(__name__).warning(
                    (
                        "Elasticsearch logging configured but NOT ACTIVE. "
                        "Проверьте доступность %s, креды и TLS."
                    ),
                    cfg.get("ELASTICSEARCH_HOST"),
                )

    # Access log middleware
    @app.before_request
    def _assign_request_id() -> None:
        """Assign a unique request ID to the Flask g context."""
        g.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    @app.after_request
    def _access_log(response: Response) -> Response:
        """Write a structured access log entry and return the response."""
        try:
            logging.getLogger("access").info(
                "HTTP %s %s -> %s",
                request.method,
                request.path,
                response.status_code,
                extra={
                    "request_id": getattr(g, "request_id", None),
                    "path": request.path,
                    "method": request.method,
                    "status_code": response.status_code,
                },
            )
        except Exception:
            pass
        response.headers["X-Request-ID"] = getattr(g, "request_id", "-") or "-"
        return response
