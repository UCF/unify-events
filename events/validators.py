from django.core.exceptions import ValidationError

from PIL import Image


def validate_max_dimensions(image, max_width, max_height, label):
    """
    Reject an uploaded image whose pixel dimensions exceed the given maximums.

    Kept in its own module rather than alongside the models so that the model
    modules can import it without pulling events.functions (and through it
    events.models) back in as a circular import.
    """
    try:
        # Deliberately not closed: PIL closes the underlying file with it, and
        # the storage backend still needs to read the upload afterwards. Size
        # comes from the header, so nothing is decoded here.
        width, height = Image.open(image).size
    except Exception:
        raise ValidationError('The file uploaded could not be read as an image.')
    finally:
        image.seek(0)

    if width > max_width or height > max_height:
        raise ValidationError(
            f'The {label} cannot exceed {max_width}x{max_height} pixels. '
            f'The image uploaded is {width}x{height} pixels.'
        )


# Each field needs its own named function: migrations serialize validators by
# import path, so a shared closure or partial cannot be written out.

def validate_calendar_desktop_header(image):
    validate_max_dimensions(image, 1600, 500, 'desktop header image')


def validate_calendar_mobile_header(image):
    validate_max_dimensions(image, 575, 575, 'mobile header image')


def validate_featured_event_desktop_image(image):
    validate_max_dimensions(image, 555, 416, 'desktop featured image')


def validate_featured_event_mobile_image(image):
    validate_max_dimensions(image, 575, 575, 'mobile featured image')
