"""In-memory репозиторий истории чата по идентификатору сессии."""

from collections import defaultdict, deque
from typing import Deque, Dict, List, Tuple


class ChatMemoryRepository:
    """Хранит последние сообщения чата, ограничивая длину истории."""

    def __init__(self, max_messages: int = 20) -> None:
        """Создаёт репозиторий с ограничением количества сообщений на сессию."""
        self._storage: Dict[str, Deque[Tuple[str, str]]] = defaultdict(
            lambda: deque(maxlen=max_messages)
        )

    def append(self, session_id: str, role: str, content: str) -> None:
        """Добавляет сообщение в историю по сессии."""
        self._storage[session_id].append((role, content))

    def get(self, session_id: str) -> List[Dict[str, str]]:
        """Возвращает историю сообщений для сессии в формате списка словарей."""
        return [
            {"role": r, "content": c}
            for r, c in list(self._storage.get(session_id, deque()))
        ]

    def clear(self, session_id: str) -> None:
        """Очищает историю сообщений для сессии."""
        self._storage.pop(session_id, None)
