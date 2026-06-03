"""
Run this script once before launching the app:
    python train.py

It trains the character-level GRU on dataset/poems.csv and saves the
model + vocabulary to models/ so app.py can load them at startup.
"""
from modules.generator import PoetryGenerator

if __name__ == "__main__":
    gen = PoetryGenerator()
    print("Training poetry model — this takes several minutes on CPU (hours without GPU).")
    gen.train()
    gen.save()
    print("Done. Model saved to models/")
