import librosa
import numpy as np
import os
import json # <-- NEW: Import the json library

# Defines the 12 Swarasthanas using precise cent values derived from the provided Hz values
# These values are RELATIVE to the tonic (Sa = 0 cents) and are tonic-independent.
SWARA_CENTERS = np.array([
    0.00,       # Sa (0)
    112.98,     # R1 (from 221.50 Hz)
    203.05,     # R2/G1 (from 233.61 Hz)
    315.64,     # R3/G2 (from 249.18 Hz)
    386.31,     # G3 (from 259.56 Hz)
    498.05,     # M1 (from 276.87 Hz)
    580.81,     # M2 (from 292.05 Hz)
    701.96,     # Pa (from 311.48 Hz)
    779.46,     # D1 (from 328.00 Hz)
    1018.00,    # D2/N1 (from 369.99 Hz)
    1035.78,    # D3/N2 (from 373.77 Hz)
    1105.74     # N3 (from 389.34 Hz)
])

# Maps the 12 indices (0-11) to the actual swara names for reporting
SWARA_NAMES = [
    "Sa (0)", "R1 (1)", "R2/G1 (2)", "R3/G2 (3)", 
    "G3 (4)", "M1 (5)", "M2 (6)", "Pa (7)", 
    "D1 (8)", "D2/N1 (9)", "D3/N2 (10)", "N3 (11)"
]

# --- Phase 1: Pitch Extraction and Swara Quantification ---

def analyze_raga_swaras(audio_path, sr=22050, tonic_freq=None):
    """Detects tonic (Sa) and quantifies all pitches into 12 Swarasthanas using precise centers."""
    y, sr = librosa.load(audio_path, sr=sr)
    
    # Robust Pitch Estimation (F0)
    f0, _, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C6'), sr=sr
    )
    
    f0 = f0[~np.isnan(f0)]
    f0 = f0[f0 > 0] 

    if len(f0) == 0:
        return 0, set(), np.array([])
    
    # 🌟 Tonic Detection: If no tonic is provided, use the median pitch from the audio
    if tonic_freq is None:
        tonic_freq = np.median(f0)  
    
    # Convert F0 to Cents relative to the provided or detected Tonic (Sa)
    cent_trajectory = 1200 * np.log2(f0 / tonic_freq)
    cent_trajectory = cent_trajectory % 1200 
    
    # Find the closest of the 12 precise Swara centers
    diff_matrix = np.abs(cent_trajectory[:, np.newaxis] - SWARA_CENTERS)
    closest_swara_indices = np.argmin(diff_matrix, axis=1)
    
    # Determine the unique set of Swarasthanas present (used for more than 1% of time)
    unique, counts = np.unique(closest_swara_indices, return_counts=True)
    total_samples = len(closest_swara_indices)
    present_swara_indices = set(unique[counts / total_samples > 0.01])
    
    return tonic_freq, present_swara_indices, cent_trajectory


# --- Phase 2: Rule-Based Raga Identification (Loads from JSON) ---

def define_ragas():
    """Loads all Raga scale definitions from the external JSON file."""
    try:
        # Determine the absolute path to the raga_data.json file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, 'raga_data.json')
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            
            raga_scales = {}
            # Convert the list of indices (from JSON) into a Python set of integers
            for name, index_list in data.items():
                raga_scales[name] = set(index_list)
                
            return raga_scales
            
    except FileNotFoundError:
        print("ERROR: raga_data.json not found! Please create it in the same directory.")
        return {}
    except Exception as e:
        print(f"ERROR loading raga data: {e}")
        return {}
    
def match_raga_set(input_swaras: set, raga_scales: dict):
    """Compares input swaras to known scales and ranks them."""
    results = []
    
    for raga_name, raga_set in raga_scales.items():
        # Score calculation: Lower score is a better match
        non_raga_notes = input_swaras - raga_set
        missing_notes = raga_set - input_swaras
        
        # High penalty for playing "wrong" notes (non-raga notes)
        score = (len(non_raga_notes) * 100) + len(missing_notes)
        
        # Use SWARA_NAMES from the top of the file for reporting
        non_raga_names = [SWARA_NAMES[i] for i in non_raga_notes]
        
        results.append({
            "raga": raga_name,
            "score": score,
            "non_raga_notes": non_raga_names,
            "missing_notes_count": len(missing_notes),
        })

    # Sort by score (lowest is best) and return top 3
    results.sort(key=lambda x: x['score'])
    return results[:3]