import numpy as np
import soundfile as sf
import mir_eval

# --- Load reference and estimated sources ---
ref_vocals, sr = sf.read("/Users/yekhaungphone/My file/Datasets/my music genre/pop/A Classic Education - NightOwl/vocals.wav")
ref_drums, _   = sf.read("/Users/yekhaungphone/My file/Datasets/my music genre/pop/A Classic Education - NightOwl/drums.wav")
est_vocals, _  = sf.read("/Users/yekhaungphone/My file/Demucs/separated_tracks/htdemucs/mixture/vocals.mp3")
est_drums, _   = sf.read("/Users/yekhaungphone/My file/Demucs/separated_tracks/htdemucs/mixture/drums.mp3")

# --- Make sure lengths match ---
min_len = min(len(ref_vocals), len(est_vocals))
ref_vocals = ref_vocals[:min_len]
est_vocals = est_vocals[:min_len]

min_len = min(len(ref_drums), len(est_drums))
ref_drums = ref_drums[:min_len]
est_drums = est_drums[:min_len]

# --- Stack into (sources x samples) ---
references = np.vstack([ref_vocals.T, ref_drums.T])
estimates  = np.vstack([est_vocals.T, est_drums.T])

# --- Compute metrics ---
sdr, sir, sar, perm = mir_eval.separation.bss_eval_sources(references, estimates)

print("SDR:", sdr)
print("SIR:", sir)
print("SAR:", sar)
print("Permutation:", perm)
