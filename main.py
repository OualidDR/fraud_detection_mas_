"""
Point d'entrée principal — Simulation temps réel du pipeline MAS.
Lit le dataset ligne par ligne et envoie chaque transaction dans le bus.
"""
import os
import logging
import pandas as pd
from tqdm import tqdm

from config           import DATA_PROC, LOGS_DIR
from core.message_bus import MessageBus
from core.messages    import Message, MessageType
from agents           import AnalyseurAgent, DetecteurAgent, AlerteAgent

# ── Logging ───────────────────────────────────────────────────────────────────
os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOGS_DIR, "mas_run.log")),
    ],
)
logger = logging.getLogger("main")


def main():
    sample_path = os.path.join(DATA_PROC, "sample_5000.csv")
    if not os.path.exists(sample_path):
        raise FileNotFoundError(
            "Dataset introuvable. Lancez d'abord : python scripts/train_model.py"
        )

    # ── 1. Initialisation du Bus ──────────────────────────────────────────────
    logger.info("Initialisation du MessageBus...")
    bus = MessageBus()

    # ── 2. Initialisation des Agents (ordre important : s'abonnent au bus) ────
    logger.info("Démarrage des agents...")
    analyseur = AnalyseurAgent(bus)   # s'abonne à NOUVELLE_TRANSACTION
    detecteur = DetecteurAgent(bus)   # s'abonne à ANALYSE_COMPLETE
    alerte    = AlerteAgent(bus)      # s'abonne à DETECTION_COMPLETE

    # ── 3. Simulation du flux de transactions ─────────────────────────────────
    df = pd.read_csv(sample_path)
    logger.info(f"Simulation de {len(df):,} transactions...")

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Transactions"):
        tx = row.to_dict()
        tx["transaction_id"] = idx
        tx["carte_id"]       = f"CARTE_{idx % 500:04d}"

        msg = Message(
            type=MessageType.NOUVELLE_TRANSACTION,
            payload=tx,
            source="Producteur",
        )
        bus.publish(msg)

    # ── 4. Résumé final ───────────────────────────────────────────────────────
    logger.info("\n" + "="*50)
    logger.info("RÉSUMÉ DE LA SESSION")
    logger.info("="*50)

    decisions = pd.DataFrame(alerte.decisions)
    comptage  = decisions["decision"].value_counts()
    for decision, count in comptage.items():
        logger.info(f"  {decision:15s} : {count:,}")

    bloquees = decisions[decisions["decision"] == "BLOQUÉE"]
    vraies_fraudes = bloquees[bloquees["vrai_label"] == 1]
    logger.info(f"\n  Fraudes réelles bloquées : {len(vraies_fraudes)} / {decisions['vrai_label'].sum()}")
    logger.info("\n📨 Messages échangés sur le bus :")
    for k, v in bus.stats().items():
        logger.info(f"   {k:25s} : {v:,}")


if __name__ == "__main__":
    main()
