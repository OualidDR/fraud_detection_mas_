"""Tests unitaires du MessageBus."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.message_bus import MessageBus
from core.messages    import Message, MessageType


def test_subscribe_et_publish():
    bus      = MessageBus()
    received = []

    def handler(msg: Message):
        received.append(msg)

    bus.subscribe(MessageType.NOUVELLE_TRANSACTION, handler)
    msg = Message(type=MessageType.NOUVELLE_TRANSACTION, payload={"test": 1}, source="test")
    bus.publish(msg)

    assert len(received) == 1
    assert received[0].payload["test"] == 1
    print("✅ test_subscribe_et_publish OK")


def test_pas_de_handler():
    bus = MessageBus()
    msg = Message(type=MessageType.NOUVELLE_TRANSACTION, payload={}, source="test")
    bus.publish(msg)  # Ne doit pas lever d'exception
    print("✅ test_pas_de_handler OK")


def test_chaine_agents_mock():
    """Vérifie la chaîne complète avec des handlers mock."""
    bus     = MessageBus()
    etapes  = []

    def step1(msg): etapes.append("analyseur"); bus.publish(Message(MessageType.ANALYSE_COMPLETE,   {}, "A"))
    def step2(msg): etapes.append("detecteur"); bus.publish(Message(MessageType.DETECTION_COMPLETE, {}, "D"))
    def step3(msg): etapes.append("alerte")

    bus.subscribe(MessageType.NOUVELLE_TRANSACTION, step1)
    bus.subscribe(MessageType.ANALYSE_COMPLETE,     step2)
    bus.subscribe(MessageType.DETECTION_COMPLETE,   step3)

    bus.publish(Message(MessageType.NOUVELLE_TRANSACTION, {}, "test"))
    assert etapes == ["analyseur", "detecteur", "alerte"], f"Chaîne incorrecte : {etapes}"
    print("✅ test_chaine_agents_mock OK")


if __name__ == "__main__":
    test_subscribe_et_publish()
    test_pas_de_handler()
    test_chaine_agents_mock()
    print("\n🎉 Tous les tests passent !")
