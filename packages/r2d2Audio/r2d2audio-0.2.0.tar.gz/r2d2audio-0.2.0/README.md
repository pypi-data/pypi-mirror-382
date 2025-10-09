# r2d2Audio

r2d2Audio es una librería experimental en Python que convierte texto en tonos, sonidos binarios y notas musicales al estilo del droide R2-D2 de Star Wars.
Está pensada para proyectos de audio, codificación sonora o demostraciones educativas sobre procesamiento de señales.

## INSTALACIÓN

Para instalar el paquete desde PyPI (una vez publicado):
```bash
pip install r2d2Audio
```

## EJEMPLO DE USO

```python
from r2d2Audio import R2D2

r2d2 = R2D2()

audio = r2d2.text_to_tones("hola mundo")

r2d2.save_audio(audio, "output.wav")
```

## CARACTERÍSTICAS

- Convierte texto en tonos de audio
- Soporta silencios entre tonos
- Decodifica tonos de vuelta a texto
- Modo binario (frecuencias para 0 y 1)
- Modo musical con notas de la escala mayor
- Permite guardar resultados en formato WAV

## REQUISITOS

- Python 3.8 o superior
- Numpy
- Scipy

Estas dependencias se instalan automáticamente con el paquete.

## EJEMPLOS ADICIONALES

Convertir texto a tonos con silencios:

```python
from r2d2Audio import R2D2

r2d2 = R2D2()
audio = r2d2.text_to_tones_with_silence("hola mundo")
r2d2.save_audio(audio, "output_silencio.wav")

#Decodificar el audio:

mensaje = r2d2.decode_tones_with_silence(audio)
print(mensaje)
```

## LICENCIA

Este proyecto está bajo la licencia MIT.
Consulta el archivo LICENSE para más detalles.

**Autor:** Edinson Tunjano