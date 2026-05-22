"""Tests unitaires des agents (sans modèle ML)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.message_bus import MessageBus
from core.messages    import Message, MessageType
from agents.analyseur_agent import AnalyseurAgent
from agents.alerte_agent    import AlerteAgent


def test_analyseur_enrichit_message():
    bus = MessageBus()
    resultats = []

    # Mock : intercepter ANALYSE_COMPLETE
    def capturer(msg): resultats.append(msg)
    bus.subscribe(MessageType.ANALYSE_COMPLETE, capturer)

    agent = AnalyseurAgent(bus)
    tx    = {"transaction_id": 1, "Amount": 250.0, "Time": 36000.0, "Class": 0}
    bus.publish(Message(MessageType.NOUVELLE_TRANSACTION, tx, "test"))

    assert len(resultats) == 1
    assert "features_risque" in resultats[0].payload
    features = resultats[0].payload["features_risque"]
    assert "montant_normalise" in features
    assert "heure" in features
    print("✅ test_analyseur_enrichit_message OK")


def test_alerte_bloque_score_eleve():
    bus   = MessageBus()
    agent = AlerteAgent(bus)

    # Simuler un message DETECTION_COMPLETE avec score très élevé
    tx  = {"transaction_id": 99, "Class": 1, "score_anomalie": 0.90,
           "features_risque": {"est_heure_nuit": True, "montant_eleve": True,
                               "velocite_10min": 1, "montant_brut": 2000.0}}
    bus.publish(Message(MessageType.DETECTION_COMPLETE, tx, "test"))

    assert agent.decisions[-1]["decision"] == "BLOQUÉE"
    print("✅ test_alerte_bloque_score_eleve OK")


def test_alerte_approuve_transaction_normale():
    bus   = MessageBus()
    agent = AlerteAgent(bus)

    tx  = {"transaction_id": 100, "Class": 0, "score_anomalie": 0.10,
           "features_risque": {"est_heure_nuit": False, "montant_eleve": False,
                               "velocite_10min": 1, "montant_brut": 30.0}}
    bus.publish(Message(MessageType.DETECTION_COMPLETE, tx, "test"))

    assert agent.decisions[-1]["decision"] == "APPROUVÉE"
    print("✅ test_alerte_approuve_transaction_normale OK")


if __name__ == "__main__":
    test_analyseur_enrichit_message()
    test_alerte_bloque_score_eleve()
    test_alerte_approuve_transaction_normale()
    print("\n🎉 Tous les tests agents passent !")
