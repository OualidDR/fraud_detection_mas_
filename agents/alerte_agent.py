"""
Agent 3 — Alerte
Responsabilité : lire le score d'anomalie + les features de risque,
appliquer les règles métier, et émettre une décision finale.
"""
import logging
from config           import SEUIL_BLOCAGE, SEUIL_AUTH, VELOCITE_MAX
from core.message_bus import MessageBus
from core.messages    import Message, MessageType

logger = logging.getLogger("AlerteAgent")


class AlerteAgent:
    """
    Décision finale : APPROUVÉE | AUTH_REQUISE | BLOQUÉE.
    Les résultats sont publiés sur DECISION_FINALE et stockés dans self.decisions.
    """

    def __init__(self, bus: MessageBus):
        self.bus       = bus
        self.decisions: list[dict] = []   # historique pour évaluation
        self.bus.subscribe(MessageType.DETECTION_COMPLETE, self._handle)
        logger.info("AlerteAgent démarré.")

    def _handle(self, msg: Message) -> None:
        tx      = msg.payload
        score   = tx.get("score_anomalie", 0.0)
        features= tx.get("features_risque", {})

        decision = self._decider(score, features)
        tx["decision"] = decision

        # Stocker pour évaluation
        self.decisions.append({
            "transaction_id": tx.get("transaction_id"),
            "vrai_label":     int(tx.get("Class", 0)),
            "score_anomalie": score,
            "decision":       decision,
        })

        out = Message(
            type=MessageType.DECISION_FINALE,
            payload=tx,
            source="AlerteAgent",
        )
        self.bus.publish(out)

        # Log visible pour les décisions critiques
        if decision != "APPROUVÉE":
            logger.warning(
                f"[Alerte] TX {tx.get('transaction_id')} → {decision} "
                f"(score={score:.3f}, montant={features.get('montant_brut', 0):.2f}€)"
            )

    def _decider(self, score: float, features: dict) -> str:
        """
        Règles métier (priorité décroissante) :
        1. Score très élevé                       → BLOQUÉE
        2. Score élevé + critère aggravant        → BLOQUÉE
        3. Score moyen OU critère aggravant seul  → AUTH_REQUISE
        4. Sinon                                  → APPROUVÉE
        """
        criteres_aggravants = (
            features.get("est_heure_nuit", False)
            or features.get("montant_eleve", False)
            or features.get("velocite_10min", 0) > VELOCITE_MAX
        )

        if score >= SEUIL_BLOCAGE:
            return "BLOQUÉE"
        if score >= SEUIL_AUTH and criteres_aggravants:
            return "BLOQUÉE"
        if score >= SEUIL_AUTH or criteres_aggravants:
            return "AUTH_REQUISE"
        return "APPROUVÉE"
