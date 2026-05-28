# 🕵️ Détection de Fraudes Bancaires — Architecture Multi-Agents (MAS)

fraud_detection_mas/
├── main.py                     ← Point d'entrée
├── config.py                   ← Tous les paramètres
├── requirements.txt
├── agents/
│   ├── analyseur_agent.py      ← Agent 1
│   ├── detecteur_agent.py      ← Agent 2
│   └── alerte_agent.py         ← Agent 3
├── core/
│   ├── message_bus.py          ← CŒUR de l'orchestration
│   └── messages.py             ← Contrat de communication
├── scripts/
│   ├── train_model.py          ← Entraînement offline
│   └── evaluate.py             ← Métriques
├── tests/
│   ├── test_message_bus.py
│   └── test_agents.py
└── data/  models/  logs/


## Architecture
```
Transaction → Agent Analyseur → Agent Détecteur → Agent Alerte → Décision
                  ↑                   ↑                 ↑
              (features)         (IsolationForest)   (règles/seuils)
                              ← Communication via MessageBus →
```

## Agents
| Agent | Rôle |
|-------|------|
| `AnalyseurAgent` | Calcule les features de risque (montant, heure, vélocité) |
| `DetecteurAgent` | Détecte les anomalies via IsolationForest (entraîné offline) |
| `AlerteAgent` | Décide : BLOQUER / AUTH_REQUISE / APPROUVÉE |

## Installation
```bash
pip install -r requirements.txt
```

## Lancement
```bash
# 1. Placer creditcard.csv dans data/raw/
# 2. Entraîner le modèle
python scripts/train_model.py

# 3. Lancer la simulation MAS temps réel
python main.py

# 4. Évaluer les performances
python scripts/evaluate.py
```

## Métriques cibles
- **Recall fraudes** > 85%
- **Precision** > 70%
- **Latence par transaction** < 50ms
# fraud_detection_mas_
