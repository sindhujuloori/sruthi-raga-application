from flask import Flask, request, jsonify
# Added warnings to help diagnose library issues
import warnings 
warnings.filterwarnings('ignore', category=FutureWarning) 

from analysis import analyze_raga_swaras, define_ragas, match_raga_set 
import numpy as np 
import os

# Define the temporary directory for file uploads
UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/analyze', methods=['POST'])
def analyze_audio():
    
    if 'audio_file' not in request.files:
        return jsonify({"error": "No 'audio_file' part in the request. Use -F 'audio_file=@...' in curl."}), 400
    
    file = request.files['audio_file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 🌟 CRITICAL FIX APPLIED HERE
    form_data = request.form
    if form_data is None:
        form_data = {}

    user_tonic_hz = form_data.get('tonic_hz')
    # ----------------------------
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    
    final_tonic_hz = 0.0

    try:
        # Phase 1: Core Analysis
        if user_tonic_hz:
            try:
                final_tonic_hz = float(user_tonic_hz)
                # Pass the user-provided tonic to the analysis function
                median_tonic, swara_set_indices, cent_trajectory = analyze_raga_swaras(filepath, tonic_freq=final_tonic_hz)
            except ValueError:
                return jsonify({"error": "Invalid format for 'tonic_hz'. Must be a number (float/int)."}), 400
        else:
            # If no tonic is provided, let the analysis function detect it
            median_tonic, swara_set_indices, cent_trajectory = analyze_raga_swaras(filepath)
            final_tonic_hz = median_tonic

        # ... (Raga Matching and return logic remains the same) ...
        raga_scales = define_ragas()
        matched_ragas = match_raga_set(swara_set_indices, raga_scales)
        
        return jsonify({
            "status": "success",
            "tonic_hz_used": f"{final_tonic_hz:.2f}",
            "swara_indices_present": [int(x) for x in sorted(list(swara_set_indices))],
            "matched_ragas": matched_ragas
        })

    except Exception as e:
        # Crucial: This should catch the librosa error and print it to the user.
        return jsonify({"error": f"Analysis failed (Check Dependencies): {str(e)}"}), 500
    
    finally:
        if os.path.exists(filepath):
            os.remove(filepath) 
        
if __name__ == '__main__':
    # Increase timeout for the server when debugging
    app.run(debug=True, host='0.0.0.0', port=8080)