"""Сервис для поиска логов в Elasticsearch.

Класс `ElasticsearchLogService` выполняет параметризованные запросы к индексу
логов в Elasticsearch и возвращает агрегированный результат для отображения.
"""

from __future__ import annotations

from typing import Any, Optional

try:
    from elasticsearch import Elasticsearch
except Exception:  # pragma: no cover
    Elasticsearch = None  # type: ignore


class ElasticsearchLogService:
    """Сервис для запросов к индексу логов в Elasticsearch."""

    def __init__(
        self,
        host: str,
        index_name: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_certs: bool = False,
        ca_certs: Optional[str] = None,
        request_timeout: int = 5,
    ) -> None:
        """Инициализировать клиент поиска логов.

        Поддерживает HTTP(S), базовую аутентификацию и проверку сертификатов.
        При ошибке инициализации переключается в отключённый режим.
        """
        self.index = index_name
        self.enabled = False
        self._es: Optional[Elasticsearch] = None
        if Elasticsearch is None:
            return
        try:
            kwargs: dict[str, Any] = {
                "hosts": [host],
                "request_timeout": request_timeout,
            }
            if host.startswith("https://"):
                kwargs["verify_certs"] = verify_certs
                if ca_certs:
                    kwargs["ca_certs"] = ca_certs
            if username and password:
                kwargs["basic_auth"] = (username, password)
            self._es = Elasticsearch(**kwargs)
            self._es.info()
            self.enabled = True
        except Exception:
            self.enabled = False
            self._es = None

    def search_logs(
        self,
        query: str | None = None,
        level: str | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
        size: int = 50,
        page: int = 0,
    ) -> dict[str, Any]:  # pragma: no cover - IO
        """Выполнить поиск логов по фильтрам и пагинации.

        Возвращает словарь с полями ``total`` и ``hits``.
        """
        if not self.enabled or self._es is None:
            return {"total": 0, "hits": []}

        must: list[dict[str, Any]] = []
        filter_clauses: list[dict[str, Any]] = []

        if query:
            must.append({"query_string": {"query": query}})
        if level:
            filter_clauses.append({"term": {"level.keyword": level.upper()}})
        if from_ts or to_ts:
            rng: dict[str, Any] = {}
            if from_ts:
                rng["gte"] = from_ts
            if to_ts:
                rng["lte"] = to_ts
            filter_clauses.append({"range": {"@timestamp": rng}})

        body = {
            "query": {
                "bool": {
                    "must": must or [{"match_all": {}}],
                    "filter": filter_clauses,
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "from": max(page, 0) * size,
            "size": size,
        }
        res = self._es.search(index=self.index, body=body)
        total = res.get("hits", {}).get("total", {}).get("value", 0)
        hits = [
            {
                "timestamp": h.get("_source", {}).get("@timestamp"),
                "level": h.get("_source", {}).get("level"),
                "logger": h.get("_source", {}).get("logger"),
                "message": h.get("_source", {}).get("message"),
                "request_id": h.get("_source", {}).get("request_id"),
                "path": h.get("_source", {}).get("path"),
                "method": h.get("_source", {}).get("method"),
                "status_code": h.get("_source", {}).get("status_code"),
            }
            for h in res.get("hits", {}).get("hits", [])
        ]
        return {"total": total, "hits": hits}
