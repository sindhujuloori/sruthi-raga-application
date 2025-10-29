import librosa
try:
    y, sr = librosa.load('uploads/test_swara.mp3', sr=None)
    print("Success! File loaded.")
except Exception as e:
    print(f"Error loading file: {e}")