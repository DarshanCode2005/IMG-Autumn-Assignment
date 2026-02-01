import qrcode
import os
from pathlib import Path
from app.core.config import settings


def generate_qr_code(url: str, event_slug: str) -> str:
    """
    Generate a QR code for the given URL and save it to media/qrcodes.
    
    Args:
        url: The URL to encode in the QR code
        event_slug: The event slug to use for the filename
    
    Returns:
        The path to the generated QR code image
    """
    # Create media/qrcodes directory if it doesn't exist
    qr_dir = Path("media/qrcodes")
    qr_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file
    filename = f"{event_slug}.png"
    filepath = qr_dir / filename
    img.save(filepath)
    
    # Return relative path
    return str(filepath)

