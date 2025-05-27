import numpy as np
import sounddevice as sd
import serial
import time

# 🎵 Audio settings
SAMPLERATE = 44100
CHUNK_SIZE = 512
DEVICE = 7  # Change this to your correct microphone index
# DEVICE =
# 🔌 Serial settings
SERIAL_PORT = "COM8"  # Check if correct
BAUD_RATE = 115200

# 🎨 Frequency Bands (Hz) - Bass, Low-Mid, Mid, High-Mid, Treble
FREQ_BANDS = [(60, 120), (170, 400), (500, 1000), (1500, 2200), (3000, 6000)]
# FREQ_BANDS = [(60, 150), (250, 500), (550, 1700), (2000, 3000), (6000, 10000)]
# Amplification Factors
# LOW_AMP = 1  # For first three bands (Bass, Low-Mid, Mid)
# HIGH_AMP = 8.0  # For High-Mid band
# EXTRA_HIGH_AMP = 12.0  # Extra amplification for Treble band
# MAX_AMP = 20.0  # Even more amplification for the last level (Treble)

LOW_AMP = 1  # For first three bands (Bass, Low-Mid, Mid)
HIGH_AMP = 25.0  # For High-Mid band
EXTRA_HIGH_AMP = 0.1  # Extra amplification for Treble band
MAX_AMP = 4.0  # Even more amplification for the last level (Treble)

# Smooth previous values
prev_levels = np.zeros(5)

# 🔌 Open Serial Connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for Arduino to initialize
    print(f"✅ Connected to {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"❌ Serial Error: {e}")
    ser = None


# 🎚️ Process Audio Input
def process_audio(indata, frames, time, status):
    global prev_levels

    if status:
        print("⚠️ Audio Error:", status)

    # Convert stereo to mono
    audio_mono = np.mean(indata, axis=1)

    # Compute FFT
    fft_output = np.abs(np.fft.rfft(audio_mono))
    fft_output /= np.max(fft_output)  # Normalize

    # Get frequency bins
    freqs = np.fft.rfftfreq(CHUNK_SIZE, 1 / SAMPLERATE)

    # Extract band values
    bar_levels = []
    for i, (low, high) in enumerate(FREQ_BANDS):
        indices = (freqs >= low) & (freqs <= high)
        avg_magnitude = np.mean(fft_output[indices]) if np.any(indices) else 0

        # Apply different amplification factors
        if i < 3:
            amp_factor = LOW_AMP
        elif i == 3:
            amp_factor = HIGH_AMP
        elif i == 4:
            amp_factor = MAX_AMP  # Maximum amplification for Treble

        amplified_level = min(int(avg_magnitude * amp_factor * 5), 5)

        # Apply Exponential Moving Average (EMA) for smoothness
        prev_levels[i] = (prev_levels[i] * 0.7) + (amplified_level * 0.3)  # Increased smoothing
        bar_levels.append(int(round(prev_levels[i])))

    # Convert to string format (e.g., "54452") and send via serial
    output_str = "".join(map(str, bar_levels)) + "\n"
    if ser:
        ser.write(output_str.encode())
        ser.flush()

    print(f"📡 Sent: {output_str.strip()}")  # Debugging output

    # Read Arduino echo back
    response = ser.readline().decode().strip()
    if response:
        print(f"✅ Arduino Received: {response}")


# 🎤 Start Audio Stream
with sd.InputStream(callback=process_audio, samplerate=SAMPLERATE, channels=2, blocksize=CHUNK_SIZE, device=DEVICE):
    print("🎶 Streaming... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(0.1)  # Faster updates for better responsiveness
    except KeyboardInterrupt:
        print("🛑 Stopping...")
