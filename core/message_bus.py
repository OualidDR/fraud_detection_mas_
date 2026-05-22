"""
MessageBus — Cœur de l'orchestration MAS.

Pattern : Publish / Subscribe synchrone.
- Chaque agent s'abonne à un ou plusieurs MessageType.
- Quand un message est publié, tous les handlers abonnés sont appelés
  dans l'ordre d'inscription.
- Thread-safe via threading.Lock pour une future extension asynchrone.
"""
import logging
import threading
from collections import defaultdict
from typing      import Callable
from .messages   import Message, MessageType

logger = logging.getLogger("MessageBus")


class MessageBus:
    """
    Bus de messages central.
    Permet le découplage total entre les agents : aucun agent ne connaît les autres.
    """

    def __init__(self):
        # canal → liste de handlers
        self._subscribers: dict[MessageType, list[Callable]] = defaultdict(list)
        self._lock   = threading.Lock()
        self._history: list[Message] = []   # optionnel : audit trail
        logger.info("MessageBus initialisé.")

    # ── API publique ──────────────────────────────────────────────────────────
    def subscribe(self, msg_type: MessageType, handler: Callable[[Message], None]) -> None:
        """Enregistre un handler pour un type de message."""
        with self._lock:
            self._subscribers[msg_type].append(handler)
        logger.debug(f"Abonnement : {handler.__self__.__class__.__name__} → {msg_type.name}")

    def publish(self, message: Message) -> None:
        """Publie un message et notifie tous les abonnés."""
        with self._lock:
            handlers = list(self._subscribers.get(message.type, []))
            self._history.append(message)

        if not handlers:
            logger.warning(f"Aucun abonné pour {message.type.name}")
            return

        for handler in handlers:
            try:
                handler(message)
            except Exception as e:
                logger.error(
                    f"Erreur dans {handler.__self__.__class__.__name__} "
                    f"lors du traitement de {message.type.name} : {e}",
                    exc_info=True,
                )

    # ── Utilitaires ───────────────────────────────────────────────────────────
    def get_history(self, msg_type: MessageType | None = None) -> list[Message]:
        """Retourne l'historique des messages (filtré par type si précisé)."""
        if msg_type is None:
            return list(self._history)
        return [m for m in self._history if m.type == msg_type]

    def reset(self) -> None:
        """Vide l'historique (utile entre deux simulations)."""
        with self._lock:
            self._history.clear()
        logger.info("Bus réinitialisé.")

    def stats(self) -> dict:
        """Statistiques sur les messages traités."""
        from collections import Counter
        counts = Counter(m.type.name for m in self._history)
        return dict(counts)
