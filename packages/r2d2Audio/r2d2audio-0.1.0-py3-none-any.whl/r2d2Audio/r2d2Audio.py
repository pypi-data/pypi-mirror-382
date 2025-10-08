import os
import numpy as np # type: ignore
from scipy.io.wavfile import write # type: ignore

class R2D2:
    def __init__(self):
        pass


    # Tono Base
    def text_to_tones(self, text, fs=44100, duration=0.2, base_freq=300, freq_step=20):
        if text == "":
            text = " "
        tones = []
        for char in text:
            freq = base_freq + ord(char) * freq_step
            t = np.linspace(0, duration, int(fs * duration), False)
            tone = 0.5 * np.sin(2 * np.pi * freq * t)
            tones.append(tone)
        return np.concatenate(tones)

    def save_audio(self, data, filename="encoded.wav", fs=44100):
        path = os.environ.get("path_audio","../") + "Audios_temp/" + filename
        data = np.int16(data * 32767)
        write(path, fs, data)
    
    def decode_audio(self, data=None, fs=44100, duration=0.2, base_freq=300, freq_step=20):
        samples_per_char = int(fs * duration)
        num_chars = len(data) // samples_per_char
        mensaje = ""
        for i in range(num_chars):
            segment = data[i*samples_per_char:(i+1)*samples_per_char]
            fft = np.fft.rfft(segment)
            freq = np.fft.rfftfreq(len(segment), 1/fs)
            peak = freq[np.argmax(np.abs(fft))]
            char_code = int(round((peak - base_freq) / freq_step))
            mensaje += chr(char_code)
        return mensaje
    

    # Tono con Silencios
    def text_to_tones_with_silence(self, text, fs=44100, duration=0.2, base_freq=300, freq_step=20, silence_duration=0.05):
        tones = []
        silence = np.zeros(int(fs * silence_duration))  # Pausa
        for char in text:
            freq = base_freq + ord(char) * freq_step
            t = np.linspace(0, duration, int(fs * duration), False)
            tone = 0.5 * np.sin(2 * np.pi * freq * t)
            tones.append(tone)
            tones.append(silence)  # Insertar silencio después de cada tono
        return np.concatenate(tones)

    def decode_tones_with_silence(self, data=None, fs=44100, duration=0.2, silence_duration=0.05, base_freq=300, freq_step=20):
        samples_per_char = int(fs * (duration + silence_duration))
        mensaje = ""
        for i in range(0, len(data), samples_per_char):
            segment = data[i:i + int(fs * duration)]  # Solo parte con tono
            if len(segment) < int(fs * duration):
                continue  # ignorar fragmentos incompletos
            # Ventana para mejorar FFT
            window = np.hanning(len(segment))
            fft = np.fft.rfft(segment * window)
            freq = np.fft.rfftfreq(len(segment), 1 / fs)
            peak = freq[np.argmax(np.abs(fft))]
            char_code = int(round((peak - base_freq) / freq_step))
            mensaje += chr(char_code)
        return mensaje
    
    # Tono con Binarios
    def text_to_binary_tones(text, fs=44100, bit_duration=0.1, low_freq=400, high_freq=800):
        tones = []
        for char in text:
            bits = format(ord(char), '08b')  # 8 bits por carácter
            for bit in bits:
                freq = high_freq if bit == '1' else low_freq
                t = np.linspace(0, bit_duration, int(fs * bit_duration), False)
                tone = 0.5 * np.sin(2 * np.pi * freq * t)
                tones.append(tone)
        return np.concatenate(tones)
    
    def decode_binary_tones(self, data=None, fs=44100, bit_duration=0.1, low_freq=400, high_freq=800):
        samples_per_bit = int(fs * bit_duration)
        bits = ""
        for i in range(0, len(data), samples_per_bit):
            segment = data[i:i + samples_per_bit]
            if len(segment) < samples_per_bit:
                continue
            fft = np.fft.rfft(segment * np.hanning(len(segment)))
            freq = np.fft.rfftfreq(len(segment), 1 / fs)
            peak = freq[np.argmax(np.abs(fft))]
            bit = '1' if abs(peak - high_freq) < abs(peak - low_freq) else '0'
            bits += bit

        # Agrupar bits en caracteres
        mensaje = ""
        for i in range(0, len(bits), 8):
            byte = bits[i:i + 8]
            if len(byte) == 8:
                mensaje += chr(int(byte, 2))
        return mensaje
    

    
    # Tono Musical
    def letter_to_note(self, char):
        scale = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
        return note_freqs[scale[ord(char) % len(scale)]]

    def text_to_musical_tones(self, text, fs=44100, duration=0.3):
        tones = []
        for char in text:
            freq = self.letter_to_note(char.upper())
            t = np.linspace(0, duration, int(fs * duration), False)
            tone = 0.5 * np.sin(2 * np.pi * freq * t)
            tones.append(tone)
        return np.concatenate(tones)
    

# Mapeo simplificado: letras → notas en la escala mayor de Do
note_freqs = {
    'C': 261.63, 'D': 293.66, 'E': 329.63,
    'F': 349.23, 'G': 392.00, 'A': 440.00, 'B': 493.88
}