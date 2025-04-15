import os

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'} #TODO SVG should be added

def item_picture_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {ext}")

    if instance.pk:
        new_filename = f"{instance.pk}{ext}"
    else:
        new_filename = f"temp{ext}"

    return f"item_pictures/{new_filename}"
