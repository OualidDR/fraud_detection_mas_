"""
Agent 2 — Détecteur
Responsabilité : charger le modèle IsolationForest pré-entraîné,
scorer chaque transaction analysée, et publier le résultat.
"""
import logging
import numpy as np
import joblib
from config       import MODEL_PATH, SCALER_PATH
from core.message_bus import MessageBus
from core.messages    import Message, MessageType

logger = logging.getLogger("DetecteurAgent")

# Colonnes PCA du dataset Kaggle (V1..V28 + Amount + Time)
PCA_COLS = [f"V{i}" for i in range(1, 29)] + ["Amount", "Time"]


class DetecteurAgent:
    """
    Applique IsolationForest sur chaque transaction enrichie.
    Publie un score d'anomalie normalisé [0, 1] (plus proche de 1 = plus suspect).
    """

    def __init__(self, bus: MessageBus):
        self.bus    = bus
        self.model  = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)
        self.bus.subscribe(MessageType.ANALYSE_COMPLETE, self._handle)
        logger.info("DetecteurAgent démarré — modèle chargé.")

    def _handle(self, msg: Message) -> None:
        tx      = msg.payload
        score   = self._scorer(tx)

        out = Message(
            type=MessageType.DETECTION_COMPLETE,
            payload={**tx, "score_anomalie": score},
            source="DetecteurAgent",
        )
        self.bus.publish(out)
        logger.debug(f"[Détecteur] TX {tx.get('transaction_id')} → score {score:.3f}")

    def _scorer(self, tx: dict) -> float:
        """
        Construit le vecteur de features, applique le scaler, puis IsolationForest.
        Retourne un score [0,1] : decision_function inversée et normalisée.
        """
        try:
            vecteur = np.array([[tx.get(col, 0.0) for col in PCA_COLS]], dtype=float)
            vecteur_scaled = self.scaler.transform(vecteur)
            # decision_function : valeurs négatives = plus anomales
            raw_score = self.model.decision_function(vecteur_scaled)[0]
            # Normalisation : plus le score brut est négatif, plus la fraude est probable
            score_normalise = float(np.clip(-raw_score + 0.5, 0.0, 1.0))
            return score_normalise
        except Exception as e:
            logger.error(f"Erreur scoring : {e}")
            return 0.0
