"""
Entraînement offline de l'IsolationForest sur creditcard.csv.
Sauvegarde le modèle et le scaler dans models/.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas  as pd
import numpy   as np
import joblib
from sklearn.ensemble        import IsolationForest
from sklearn.preprocessing   import StandardScaler
from sklearn.model_selection import train_test_split
from config import (
    DATA_RAW, MODEL_PATH, SCALER_PATH,
    IF_CONTAMINATION, IF_N_ESTIMATORS, IF_RANDOM_STATE, DATA_PROC
)

def main():
    # ── 1. Chargement ─────────────────────────────────────────────────────────
    print(" Chargement du dataset...")
    df = pd.read_csv(DATA_RAW)
    print(f"   {len(df):,} transactions — {df['Class'].sum()} fraudes "
          f"({df['Class'].mean()*100:.3f}%)")

    # ── 2. Split train / test AVANT toute normalisation ───────────────────────
    print("  Split train/test (98% / 2%) stratifié...")
    df_train, df_test = train_test_split(
        df,
        test_size=0.02,
        random_state=IF_RANDOM_STATE,
        stratify=df["Class"]   # garantit des fraudes dans les 2 parties
    )
    print(f"   Train : {len(df_train):,} lignes — "
          f"{df_train['Class'].sum()} fraudes")
    print(f"   Test  : {len(df_test):,} lignes  — "
          f"{df_test['Class'].sum()} fraudes")

    # ── 3. Normalisation (fitté sur train uniquement) ─────────────────────────
    features = [f"V{i}" for i in range(1, 29)] + ["Amount", "Time"]
    X_train  = df_train[features].values

    print("  Normalisation (StandardScaler fitté sur train uniquement)...")
    scaler        = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # ── 4. Entraînement sur transactions normales du train uniquement ─────────
    print(f" Entraînement IsolationForest "
          f"(n_estimators={IF_N_ESTIMATORS}, contamination={IF_CONTAMINATION})...")
    X_normal = X_train_scaled[df_train["Class"] == 0]
    model = IsolationForest(
        n_estimators=IF_N_ESTIMATORS,
        contamination=IF_CONTAMINATION,
        random_state=IF_RANDOM_STATE,
        n_jobs=-1,
    )
    model.fit(X_normal)
    print(f"   Entraîné sur {len(X_normal):,} transactions normales.")

    # ── 5. Sauvegarde du modèle et du scaler ──────────────────────────────────
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model,  MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f" Modèle sauvegardé  : {MODEL_PATH}")
    print(f" Scaler sauvegardé  : {SCALER_PATH}")

    # ── 6. Échantillon test tiré de df_test (jamais vu par le modèle) ─────────
    os.makedirs(DATA_PROC, exist_ok=True)
    sample = df_test.sample(n=min(5000, len(df_test)), random_state=IF_RANDOM_STATE)
    sample.to_csv(os.path.join(DATA_PROC, "sample_5000.csv"), index=False)
    print(f" Échantillon test   : {DATA_PROC}/sample_5000.csv")
    print(f"   ({sample['Class'].sum()} fraudes dans l'échantillon — "
          f"jamais vues pendant l'entraînement)")

if __name__ == "__main__":
    main()