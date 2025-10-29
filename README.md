# 🎵 Carnatic Raga Detection API

This is a **RESTful API** designed to analyze uploaded audio of a single Carnatic music passage and predict the likely Raga (scale) by identifying the set of *swaras* (notes) present.

The core service is built on Flask and utilizes the `librosa` library for pitch detection and swara mapping relative to a given or detected tonic (Sruthi).

### Key Features

* **Audio Upload:** Accepts a standard audio file (e.g., `.wav`, `.mp3`) for analysis.
* **Tonic Handling:** Automatically estimates the tonic frequency (Sa) if one is not explicitly provided.
* **Swara Identification:** Maps detected pitches to the 12 standard Swara indices (0-11).
* **Raga Matching:** Compares the detected swara set against a database of Carnatic Ragas (Melakarta and Janya) and provides a ranked list of matches.

---

### API Endpoint: `/analyze` (POST)

The API has one primary endpoint. It accepts **POST** requests via form-data.

| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `audio_file` | File | **Yes** | The audio file to analyze. (e.g., use `-F 'audio_file=@...'` in `curl`). |
| `tonic_hz` | Form Data (Float) | No | **Optional.** The known frequency (in Hz) of the tonic (Sa). Providing this improves accuracy. |

### Example Request (Bash/cURL)

**With API-detected Tonic:**

```bash
curl -X POST \
  -F 'audio_file=@test_swara.mp3' \
  https://[YOUR_API_DOMAIN]/analyze


Example JSON Response
A successful analysis returns a JSON object containing the determined tonic, the unique set of swaras found, and a ranked list of matching ragas.

{
  "status": "success",
  "tonic_hz_used": "240.51",
  "swara_indices_present": [0, 2, 4, 7, 9],
  "matched_ragas": [
    {
      "raga_name": "Mohanam",
      "match_score": 0,
      "non_raga_notes": [],
      "missing_raga_notes": []
    },
    {
      "raga_name": "Shankarabharanam (M29)",
      "match_score": 3,
      "non_raga_notes": [],
      "missing_raga_notes": [5, 11]
    }
  ]
}
