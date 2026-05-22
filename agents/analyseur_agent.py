"""
Agent 1 — Analyseur
Responsabilité : recevoir une transaction brute, calculer ses features de risque,
puis publier un message enrichi sur le bus.
"""
import logging
from datetime import datetime
from core.message_bus import MessageBus
from core.messages    import Message, MessageType

logger = logging.getLogger("AnalyseurAgent")


class AnalyseurAgent:
    """
    Transforme une transaction brute en vecteur de features de risque.
    Publie sur le canal ANALYSE_COMPLETE.
    """

    def __init__(self, bus: MessageBus):
        self.bus = bus
        self._historique: dict[str, list] = {}   # carte → liste de timestamps récents
        # S'abonne aux transactions entrantes
        self.bus.subscribe(MessageType.NOUVELLE_TRANSACTION, self._handle)
        logger.info("AnalyseurAgent démarré.")

    # ── Handler principal ──────────────────────────────────────────────────────
    def _handle(self, msg: Message) -> None:
        tx = msg.payload
        features = self._calculer_features(tx)

        out = Message(
            type=MessageType.ANALYSE_COMPLETE,
            payload={**tx, "features_risque": features},
            source="AnalyseurAgent",
        )
        self.bus.publish(out)
        logger.debug(f"[Analyseur] TX {tx.get('transaction_id')} → features {features}")

    # ── Calcul des features ────────────────────────────────────────────────────
    def _calculer_features(self, tx: dict) -> dict:
        montant  = float(tx.get("Amount", 0))
        heure    = self._heure_depuis_time(float(tx.get("Time", 0)))
        carte_id = tx.get("carte_id", "unknown")

        # Vélocité : nb de tx dans les 10 dernières minutes simulées
        velocite = self._calculer_velocite(carte_id, float(tx.get("Time", 0)))

        return {
            "montant_normalise": min(montant / 5000.0, 1.0),  # normalisation 0-1
            "heure":             heure,
            "est_heure_nuit":    self._est_nuit(heure),
            "montant_eleve":     montant > 1000.0,
            "velocite_10min":    velocite,
            "montant_brut":      montant,
        }

    @staticmethod
    def _heure_depuis_time(seconds: float) -> int:
        """Convertit le champ Time (secondes depuis début du dataset) en heure 0-23."""
        return int((seconds % 86400) // 3600)

    @staticmethod
    def _est_nuit(heure: int) -> bool:
        from config import HEURE_NUIT_DEBUT, HEURE_NUIT_FIN
        return HEURE_NUIT_DEBUT <= heure <= HEURE_NUIT_FIN

    def _calculer_velocite(self, carte_id: str, time_sec: float) -> int:
        """Compte les transactions des 600 dernières secondes simulées pour cette carte."""
        fenetre = 600.0
        historique = self._historique.setdefault(carte_id, [])
        historique.append(time_sec)
        # Garder uniquement la fenêtre glissante
        self._historique[carte_id] = [t for t in historique if time_sec - t <= fenetre]
        return len(self._historique[carte_id])
