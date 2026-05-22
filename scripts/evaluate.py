"""
Évaluation des performances du système MAS sur l'échantillon de test.
Affiche : Recall, Precision, F1, matrice de confusion.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sklearn.metrics import (
    classification_report, confusion_matrix, recall_score, roc_auc_score
)
from core.message_bus import MessageBus
from core.messages    import Message, MessageType
from agents           import AnalyseurAgent, DetecteurAgent, AlerteAgent
from config           import DATA_PROC
from tqdm             import tqdm


def main():
    sample_path = os.path.join(DATA_PROC, "sample_5000.csv")
    print(f"📂 Chargement de {sample_path}...")
    df = pd.read_csv(sample_path)

    # Initialisation du MAS
    bus      = MessageBus()
    analyseur= AnalyseurAgent(bus)
    detecteur= DetecteurAgent(bus)
    alerte   = AlerteAgent(bus)

    print(f"▶️  Simulation de {len(df):,} transactions...")
    for idx, row in tqdm(df.iterrows(), total=len(df)):
        tx = row.to_dict()
        tx["transaction_id"] = idx
        tx["carte_id"]       = f"CARTE_{idx % 500:04d}"  # carte simulée
        msg = Message(type=MessageType.NOUVELLE_TRANSACTION, payload=tx, source="Simulation")
        bus.publish(msg)

    # Résultats
    results = pd.DataFrame(alerte.decisions)
    y_true  = results["vrai_label"]
    # Binarisation : BLOQUÉE → 1 (fraude), autres → 0
    y_pred  = (results["decision"] == "BLOQUÉE").astype(int)

    print("\n" + "="*50)
    print("📊 RAPPORT DE PERFORMANCE DU SYSTÈME MAS")
    print("="*50)
    print(classification_report(y_true, y_pred, target_names=["Normal", "Fraude"]))

    cm = confusion_matrix(y_true, y_pred)
    print("Matrice de confusion :")
    print(f"  VN={cm[0,0]:5d}  FP={cm[0,1]:5d}")
    print(f"  FN={cm[1,0]:5d}  VP={cm[1,1]:5d}")

    recall = recall_score(y_true, y_pred, zero_division=0)
    print(f"\n🎯 Recall fraudes : {recall*100:.1f}% {'✅' if recall > 0.85 else '❌ (cible: >85%)'}")

    print("\n📨 Statistiques du bus :")
    for k, v in bus.stats().items():
        print(f"   {k:25s} : {v:,} messages")

if __name__ == "__main__":
    main()
