from pathlib import Path
from PIL import Image

THUMBNAIL_SIZE = (50, 50)
THUMBNAIL_SUFFIX = "_thumb"
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}


def generate_thumbnail(original_path: Path, destination_paht: Path) -> str:
    # if original_path.suffix.lower() not in SUPPORTED_FORMATS:
    #     return None

    thumb_name = f"{original_path.stem}{THUMBNAIL_SUFFIX}{original_path.suffix}"
    thumb_path = destination_paht / thumb_name

    with Image.open(original_path) as img:
        img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "P") and thumb_path.suffix.lower() in {".jpg", ".jpeg"}:
            img = img.convert("RGB")

        img.save(
            thumb_path,
            optimize=True,
            quality=75,
        )

    return thumb_name
