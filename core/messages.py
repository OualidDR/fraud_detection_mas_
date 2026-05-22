"""
Définition des types de messages et de l'objet Message.
C'est le contrat de communication entre tous les agents.
"""
from enum      import Enum, auto
from dataclasses import dataclass, field
from datetime  import datetime
from typing    import Any


class MessageType(Enum):
    """Canaux de communication du bus."""
    NOUVELLE_TRANSACTION = auto()   # Transaction brute entrante
    ANALYSE_COMPLETE     = auto()   # Transaction enrichie par l'Analyseur
    DETECTION_COMPLETE   = auto()   # Transaction scorée par le Détecteur
    DECISION_FINALE      = auto()   # Décision émise par l'Alerte


@dataclass
class Message:
    """Enveloppe standard pour tous les échanges inter-agents."""
    type:      MessageType
    payload:   dict
    source:    str               = "unknown"
    timestamp: datetime          = field(default_factory=datetime.utcnow)
    metadata:  dict[str, Any]    = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"Message(type={self.type.name}, source={self.source}, "
            f"ts={self.timestamp.strftime('%H:%M:%S.%f')[:-3]})"
        )
