import io
from PIL import Image

THUMBNAIL_SIZE = (50, 50)
THUMBNAIL_SUFFIX = "_thumb"
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}


def generate_thumbnail(
    image_bytes: bytes, suffix: str, size: tuple[int, int] = (128, 128)
) -> bytes:
    """
    Genera la miniatura de una imagen a partir de sus bytes y retorna los bytes resultantes.

    :param image_bytes: Los bytes de la imagen original.
    :param suffix: La extensión del archivo (ej. '.jpg', '.png', 'webp').
    :param size: Tupla (ancho, alto) con las dimensiones máximas de la miniatura.
    :return: Los bytes de la imagen en miniatura.
    """
    # Normalizar el formato eliminando el punto si viene incluido (ej. '.png' -> 'png')
    # Pillow prefiere 'JPEG' en lugar de 'JPG' para guardar
    fmt = suffix.lstrip(".").upper()
    if fmt == "JPG":
        fmt = "JPEG"

    # Leer los bytes de entrada en memoria
    input_stream = io.BytesIO(image_bytes)

    with Image.open(input_stream) as img:
        # thumbnail() modifica la imagen in-place manteniendo la relación de aspecto
        img.thumbnail(size)

        # Guardar el resultado en un buffer de memoria
        output_stream = io.BytesIO()

        # Si es JPEG, podemos optimizarlo; si es PNG o WEBP, conserva su formato nativo
        if fmt == "JPEG":
            img.save(output_stream, format=fmt, quality=85, optimize=True)
        else:
            img.save(output_stream, format=fmt)

        return output_stream.getvalue()
