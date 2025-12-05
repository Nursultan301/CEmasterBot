from fastapi import UploadFile

from core.exceptions import ValidationException


def image_file_dep(file: UploadFile) -> UploadFile:
    if not file.file or not file.filename:
        raise ValidationException(
            error_code="value_error",
            detail="File not found!",
            attr="uploaded_file",
        )
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise ValidationException(
            error_code="value_error",
            detail="File type not supported!",
            attr="uploaded_file",
        )
    return file
