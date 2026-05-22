"""
Entraînement offline de l'IsolationForest sur creditcard.csv.
Sauvegarde le modèle et le scaler dans models/.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas  as pd
import numpy   as np
import joblib
from sklearn.ensemble      import IsolationForest
from sklearn.preprocessing import StandardScaler
from config import (
    DATA_RAW, MODEL_PATH, SCALER_PATH,
    IF_CONTAMINATION, IF_N_ESTIMATORS, IF_RANDOM_STATE, DATA_PROC
)

def main():
    print("📂 Chargement du dataset...")
    df = pd.read_csv(DATA_RAW)
    print(f"   {len(df):,} transactions — {df['Class'].sum()} fraudes "
          f"({df['Class'].mean()*100:.3f}%)")

    features = [f"V{i}" for i in range(1, 29)] + ["Amount", "Time"]
    X = df[features].values

    print("⚙️  Normalisation (StandardScaler)...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print(f"🌲 Entraînement IsolationForest "
          f"(n_estimators={IF_N_ESTIMATORS}, contamination={IF_CONTAMINATION})...")
    model = IsolationForest(
        n_estimators=IF_N_ESTIMATORS,
        contamination=IF_CONTAMINATION,
        random_state=IF_RANDOM_STATE,
        n_jobs=-1,
    )
    # Entraîner uniquement sur les transactions normales (unsupervised)
    X_normal = X_scaled[df["Class"] == 0]
    model.fit(X_normal)
    print(f"   Entraîné sur {len(X_normal):,} transactions normales.")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"✅ Modèle sauvegardé  : {MODEL_PATH}")
    print(f"✅ Scaler sauvegardé  : {SCALER_PATH}")

    # Sauvegarde d'un échantillon pour les tests
    os.makedirs(DATA_PROC, exist_ok=True)
    sample = df.sample(n=min(5000, len(df)), random_state=42)
    sample.to_csv(os.path.join(DATA_PROC, "sample_5000.csv"), index=False)
    print(f"✅ Échantillon test   : {DATA_PROC}/sample_5000.csv")

if __name__ == "__main__":
    main()
