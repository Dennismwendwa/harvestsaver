from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image

def validate_image_size(image):
    """
    Validates uploaded images by checking:
    1. The file is a real image (not corrupted).
    2. The image meets minimum and maximum resolution requirements.
    3. The file stream is rewound after inspection so Django can save it correctly.
    """

    try:
        img = Image.open(image)
        width, height = img.size
    except Exception:
        raise ValidationError(_("Invalid image file"))
    finally:
        image.seek(0)

    min_w, min_h = 600, 600
    max_w, max_h = 2500, 2500

    if width < min_w or height < min_h:
        raise ValidationError(
            _(f"Image must be at least {min_w}x{min_h}px")
        )
    
    if width > max_w or height > max_h:
        raise ValidationError(
            _(f"Image must be at most {max_w}x{max_h}px")
        )

    
def validate_image_file_size(image):
    max_size_mb = 5
    if image.size > max_size_mb * 1024 *  1024:
        raise ValidationError(
            _("Image file too large (max 5MB)")
        )
