from __future__ import annotations
import json
import logging
import socket
from datetime import datetime
from typing import Any, Optional

try:
    # elasticsearch 8+ client name remains 'elasticsearch'
    from elasticsearch import Elasticsearch
except Exception:  # pragma: no cover
    Elasticsearch = None  # type: ignore


class ElasticsearchHandler(logging.Handler):
    """
    Логгер-обработчик, отправляющий записи в Elasticsearch индекс.
    Безопасно деградирует, если клиент недоступен.
    """

    def __init__(
        self,
        es_host: str,
        index_name: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_certs: bool = False,
        ca_certs: Optional[str] = None,
        request_timeout: int = 5,
        level: int = logging.INFO,
    ) -> None:
        super().__init__(level)
        self.index_name = index_name
        self.hostname = socket.gethostname()
        self.enabled = False
        self._es: Optional[Elasticsearch] = None

        if Elasticsearch is None:
            return

        try:
            kwargs: dict[str, Any] = {"hosts": [es_host], "request_timeout": request_timeout}
            # TLS options
            if es_host.startswith("https://"):
                kwargs["verify_certs"] = verify_certs
                if ca_certs:
                    kwargs["ca_certs"] = ca_certs
            if username and password:
                kwargs["basic_auth"] = (username, password)
            self._es = Elasticsearch(**kwargs)
            # simple health check
            self._es.info()
            self.enabled = True
        except Exception:
            # Не валим приложение, просто отключаем отправку в ES
            self.enabled = False
            self._es = None

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - IO bound
        if not self.enabled or self._es is None:
            return
        try:
            doc = self._serialize(record)
            self._es.index(index=self.index_name, document=doc)
        except Exception:
            # проглатываем ошибки отправки в ES, чтобы не ломать приложение
            pass

    def _serialize(self, record: logging.LogRecord) -> dict[str, Any]:
        # Преобразуем LogRecord в JSON-документ
        return {
            "@timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "funcName": record.funcName,
            "process": record.process,
            "thread": record.thread,
            "hostname": self.hostname,
            # Доп. поля из extra
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
            "path": getattr(record, "path", None),
            "method": getattr(record, "method", None),
            "status_code": getattr(record, "status_code", None),
        }
