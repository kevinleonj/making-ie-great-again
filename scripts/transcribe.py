"""Transcribe the 30s reference audio clips using Qwen3-ASR."""

from mlx_audio.stt import load

model = load("mlx-community/Qwen3-ASR-0.6B-8bit")

print("=== TRUMP ===")
trump = model.generate("data/trump_30s.wav", language="English")
print(trump)

print("\n=== MADURO ===")
maduro = model.generate("data/maduro_30s.wav", language="Spanish")
print(maduro)
