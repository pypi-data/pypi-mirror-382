import io

import PIL.Image
from PIL.Image import Image
from timezonefinder import TimezoneFinder

timezone_finder = TimezoneFinder()


def pil_to_jpeg(pil_image: Image) -> Image:
    """Convert a PIL image to a JPEG image."""
    if pil_image.format == "GIF":
        pil_image = pil_image.convert("RGB")

    # Weird conversion to jpg so pytesseract can handle the image
    img_byte_arr = io.BytesIO()
    pil_image.save(img_byte_arr, format="JPEG")
    img_byte_arr.seek(0)
    jpeg_data = img_byte_arr.getvalue()
    return PIL.Image.open(io.BytesIO(jpeg_data))
