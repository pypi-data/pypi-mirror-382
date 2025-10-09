import numpy as np
import wave
import math
import binascii

# ====== Parámetros ajustables ======
SAMPLE_RATE = 44100    # Hz
BASE_FREQ = 100.0       # frecuencia para el byte 0 (Hz)
STEP_HZ = 10.0          # separación de frecuencia por valor de byte (Hz)
TONE_DURATION = 0.1    # segundos por símbolo (byte)
AMPLITUDE = 0.5        # 0..1
FADE_FRAC = 0.01       # fracción del tono para fade in/out (evita clicks)
# ===================================

class R2D2():
  def __init__(self):
    pass

  def synth_tone(self, freq, duration=TONE_DURATION, sample_rate=SAMPLE_RATE, amplitude=AMPLITUDE):
      t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
      tone = amplitude * np.sin(2 * np.pi * freq * t)
      nfade = max(1, int(len(t) * FADE_FRAC))
      tone[:nfade] *= np.linspace(0,1,nfade)
      tone[-nfade:] *= np.linspace(1,0,nfade)
      return tone

  def save_wav(self, filename, samples, sample_rate=SAMPLE_RATE):
      samples_clipped = np.clip(samples, -1.0, 1.0)
      int_samples = (samples_clipped * 32767).astype(np.int16)
      with wave.open(filename, 'wb') as wf:
          wf.setnchannels(1)
          wf.setsampwidth(2)
          wf.setframerate(sample_rate)
          wf.writeframes(int_samples.tobytes())

  def text_to_tones(self, text, out_path,
                        sample_rate=SAMPLE_RATE,
                        base_freq=BASE_FREQ,
                        step_hz=STEP_HZ,
                        tone_duration=TONE_DURATION):
      """
      Codifica texto (utf-8) a WAV. Prepende un header de 4 bytes con la longitud del payload.
      """
      data = text.encode('utf-8')
      header = len(data).to_bytes(4, 'big')
      payload = header + data
      samples = np.array([], dtype=float)
      for b in payload:
          f = base_freq + b * step_hz
          tone = self.synth_tone(f, duration=tone_duration, sample_rate=sample_rate)
          samples = np.concatenate((samples, tone))
      samples = np.concatenate((samples, np.zeros(int(0.02 * sample_rate))))  # pequeño silencio final
      self.save_wav(out_path, samples, sample_rate=sample_rate)
      crc = binascii.crc32(data) & 0xffffffff
      return {'out_path': out_path, 'length_bytes': len(data), 'crc32': crc}

  def detect_symbol_fft(self, block, sample_rate, base_freq=BASE_FREQ, step_hz=STEP_HZ):
      """
      Detecta la frecuencia dominante con FFT y la mapea al byte más cercano.
      Incluye interpolación cuadrática del pico para mayor precisión.
      """
      window = np.hanning(len(block))
      block_win = block * window
      N = len(block_win)
      spectrum = np.abs(np.fft.rfft(block_win))
      freqs = np.fft.rfftfreq(N, d=1.0/sample_rate)
      peak_idx = int(np.argmax(spectrum))
      # interpolación cuadrática del pico (mejora la estimación de frecuencia)
      if 1 <= peak_idx < len(spectrum)-1:
          alpha = spectrum[peak_idx-1]
          beta  = spectrum[peak_idx]
          gamma = spectrum[peak_idx+1]
          p = 0.5*(alpha - gamma) / (alpha - 2*beta + gamma)
          peak_freq = freqs[peak_idx] + p * (freqs[1]-freqs[0])
      else:
          peak_freq = freqs[peak_idx]
      b = int(round((peak_freq - base_freq) / step_hz))
      b = max(0, min(255, b))
      return b, peak_freq, spectrum[peak_idx]

  def decode_audio(self, wav_path,
                        sample_rate=SAMPLE_RATE,
                        base_freq=BASE_FREQ,
                        step_hz=STEP_HZ,
                        tone_duration=TONE_DURATION,
                        expected_max_bytes=10000):
      """
      Decodifica un WAV creado por encode_text_to_wav.
      IMPORTANTE: Debes usar los mismos sample_rate, base_freq, step_hz y tone_duration.
      """
      with wave.open(wav_path, 'rb') as wf:
          assert wf.getnchannels() == 1, "WAV debe ser mono"
          sr = wf.getframerate()
          assert sr == sample_rate, f"Sample rate mismatch: {sr} != {sample_rate}"
          raw = wf.readframes(wf.getnframes())
          samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0

      chunk_size = int(sample_rate * tone_duration)
      n_chunks = len(samples) // chunk_size
      detected = []
      for i in range(n_chunks):
          start = i*chunk_size
          block = samples[start:start+chunk_size]
          if len(block) < chunk_size:
              break
          if np.max(np.abs(block)) < 0.001:  # silencio -> fin
              break
          b, pf, mag = self.detect_symbol_fft(block, sample_rate, base_freq=base_freq, step_hz=step_hz)
          detected.append(b)
          if len(detected) > 4 + expected_max_bytes:
              break

      if len(detected) < 4:
          raise ValueError("No se encontró header válido")

      header_bytes = bytes(detected[:4])
      data_len = int.from_bytes(header_bytes, 'big')
      payload = bytes(detected[4:4+data_len])
      try:
          text = payload.decode('utf-8')
      except:
          text = None
      crc = binascii.crc32(payload) & 0xffffffff
      return {'detected_length': data_len, 'text': text, 'raw_bytes': payload, 'crc32': crc, 'detected_bytes_count': len(detected)}
 