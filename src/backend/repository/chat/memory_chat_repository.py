"""
Памятный (in-memory) репозиторий истории чата.
Хранит короткую историю сообщений по идентификатору сессии.
"""
from collections import defaultdict, deque
from typing import Deque, Dict, List, Tuple


class ChatMemoryRepository:
    """
    Репозиторий для хранения последних сообщений чата.
    Ограничивает длину истории, чтобы не расходовать память.
    """

    def __init__(self, max_messages: int = 20):
        """Создаёт репозиторий с ограничением количества сообщений на сессию."""
        self._storage: Dict[str, Deque[Tuple[str, str]]] = defaultdict(lambda: deque(maxlen=max_messages))

    def append(self, session_id: str, role: str, content: str) -> None:
        """Добавляет сообщение в историю по сессии."""
        self._storage[session_id].append((role, content))

    def get(self, session_id: str) -> List[Dict[str, str]]:
        """Возвращает историю сообщений для сессии в формате списка словарей."""
        return [{"role": r, "content": c} for r, c in list(self._storage.get(session_id, deque()))]

    def clear(self, session_id: str) -> None:
        """Очищает историю сообщений для сессии."""
        self._storage.pop(session_id, None)
