"""
Voiceover Generator for AI Knowledge Distillation Video
Uses Kokoro-ONNX v1.0 (af_heart voice) to generate high-quality deterministic TTS audio.
"""

import os
import sys
import json
import urllib.request
import shutil
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

MODEL_NAME = "kokoro-v1.0.onnx"
VOICES_NAME = "voices-v1.0.bin"

MODEL_URL = f"https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/{MODEL_NAME}"
VOICES_URL = f"https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/{VOICES_NAME}"

# Search candidates for pre-downloaded models
CANDIDATE_PATHS = [
    os.path.join("models", MODEL_NAME),
    MODEL_NAME,
    r"D:\PROJECTS\yt\hist\4okt26\kokoro_models\kokoro-v1.0.onnx",
]
VOICE_CANDIDATE_PATHS = [
    os.path.join("models", VOICES_NAME),
    VOICES_NAME,
    r"D:\PROJECTS\yt\hist\4okt26\kokoro_models\voices-v1.0.bin",
]

def download_with_progress(url, dest_path):
    print(f"Downloading {os.path.basename(dest_path)} from GitHub Releases...")
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    
    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = downloaded / total_size * 100
            mb = downloaded / (1024 * 1024)
            total_mb = total_size / (1024 * 1024)
            sys.stdout.write(f"\r  Progress: {percent:5.1f}% ({mb:5.1f} / {total_mb:5.1f} MB)")
            sys.stdout.flush()

    urllib.request.urlretrieve(url, dest_path, reporthook=report_progress)
    print()

def resolve_model_files():
    model_file = None
    for path in CANDIDATE_PATHS:
        if os.path.exists(path) and os.path.getsize(path) > 100_000_000:
            model_file = path
            break
            
    voices_file = None
    for path in VOICE_CANDIDATE_PATHS:
        if os.path.exists(path) and os.path.getsize(path) > 10_000_000:
            voices_file = path
            break

    # If missing, download to models/
    os.makedirs("models", exist_ok=True)
    if not model_file:
        model_file = os.path.join("models", MODEL_NAME)
        download_with_progress(MODEL_URL, model_file)
    if not voices_file:
        voices_file = os.path.join("models", VOICES_NAME)
        download_with_progress(VOICES_URL, voices_file)

    print(f"[OK] Model:  {model_file}")
    print(f"[OK] Voices: {voices_file}")
    return model_file, voices_file

def main():
    model_file, voices_file = resolve_model_files()

    print("\nInitializing Kokoro-ONNX...")
    kokoro = Kokoro(model_file, voices_file)

    scenes = [
        {
            "id": "scene_1",
            "name": "Hook & The Big Robot",
            "text": "Imagine this. There is a giant robot who is super smart. Why? Because it has read millions of books! But... it's huge, drains massive amounts of power, and runs really slow."
        },
        {
            "id": "scene_2",
            "name": "The Small Robot",
            "text": "Then, there's a tiny robot. It wants to be smart too, but it simply cannot read millions of books."
        },
        {
            "id": "scene_3",
            "name": "The Question",
            "text": "So, how does it do it? It learns directly from the big robot!"
        },
        {
            "id": "scene_4",
            "name": "The 3 Steps",
            "text": "Here is how: First, we ask the giant robot tons of questions. Second, the tiny robot observes every single answer. Third, it mimics how the big robot thinks and responds. And boom! The tiny robot is now super smart, almost like the big one!"
        },
        {
            "id": "scene_5",
            "name": "The Sibling Analogy",
            "text": "It's just like a younger kid learning from an older sibling. No need to start from zero—just learn the smart shortcuts!"
        },
        {
            "id": "scene_6",
            "name": "Why It Matters",
            "text": "Why does this matter? Because the tiny robot can fit right on your smartphone, responds in a flash, and costs almost nothing to run."
        },
        {
            "id": "scene_7",
            "name": "Outro & Knowledge Distillation",
            "text": "In AI, this is called Knowledge Distillation. It's how massive reasoning models like DeepSeek-R1 get compressed into lightweight models you can run anywhere."
        }
    ]

    os.makedirs("audio", exist_ok=True)
    all_samples = []
    sample_rate = 24000
    fps = 30

    timing_manifest = []
    current_time = 0.0

    print("\nGenerating voiceover clips with 'af_heart' voice...")

    for scene in scenes:
        print(f"  -> [{scene['id']}] {scene['name']}...")
        samples, sr = kokoro.create(scene["text"], voice="af_heart", speed=1.0, lang="en-us")
        sample_rate = sr
        duration = len(samples) / sr

        scene_filename = os.path.join("audio", f"{scene['id']}.wav")
        sf.write(scene_filename, samples, sr)

        start_time = current_time
        end_time = current_time + duration

        timing_manifest.append({
            "scene_id": scene["id"],
            "name": scene["name"],
            "text": scene["text"],
            "audio_file": scene_filename.replace("\\", "/"),
            "start_time": round(start_time, 2),
            "end_time": round(end_time, 2),
            "duration": round(duration, 2),
            "start_frame_30fps": int(round(start_time * fps)),
            "duration_frames_30fps": int(round(duration * fps))
        })

        all_samples.append(samples)
        # 0.3s breathing room between scenes
        pause = np.zeros(int(0.3 * sr), dtype=samples.dtype)
        all_samples.append(pause)
        current_time = end_time + 0.3

    # Merge full master audio
    full_audio = np.concatenate(all_samples)
    full_duration = len(full_audio) / sample_rate
    master_path = os.path.join("audio", "full_voiceover.wav")
    sf.write(master_path, full_audio, sample_rate)

    # Keep a copy in root for composition convenience
    shutil.copy2(master_path, "full_voiceover.wav")

    manifest_data = {
        "voice": "af_heart",
        "sample_rate": sample_rate,
        "total_duration": round(full_duration, 2),
        "total_frames_30fps": int(round(full_duration * fps)),
        "scenes": timing_manifest
    }

    with open("timing.json", "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print("\n[SUCCESS] Voiceovers generated successfully!")
    print(f"Total Duration: {full_duration:.2f}s ({manifest_data['total_frames_30fps']} frames @ 30fps)")
    print(f"Master Audio:   {master_path}")
    print(f"Timing Manifest: timing.json")

if __name__ == "__main__":
    main()
