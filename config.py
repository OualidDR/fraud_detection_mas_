"""Configuration globale du projet MAS."""
import os

# Chemins
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_RAW   = os.path.join(BASE_DIR, "data", "raw", "creditcard.csv")
DATA_PROC  = os.path.join(BASE_DIR, "data", "processed")
MODEL_PATH = os.path.join(BASE_DIR, "models", "isolation_forest.joblib")
SCALER_PATH= os.path.join(BASE_DIR, "models", "scaler.joblib")
LOGS_DIR   = os.path.join(BASE_DIR, "logs")

# Paramètres du détecteur (IsolationForest)
IF_CONTAMINATION  = 0.002   # ~0.172% arrondi légèrement
IF_N_ESTIMATORS   = 100
IF_RANDOM_STATE   = 42

# Seuils de l'agent Alerte
SEUIL_BLOCAGE  = 0.45
SEUIL_AUTH     = 0.30
MONTANT_SUSPECT = 500.0 
HEURE_NUIT_DEBUT  = 1       # 01h00
HEURE_NUIT_FIN    = 5       # 05h00
VELOCITE_MAX      = 5       # nb transactions / 10 min max avant alerte

# Message Bus
BUS_MAX_SIZE = 1000         # taille max de la file d'attente
