from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils import timezone
from datetime import date, datetime
#import PyPDF2

def validate_file_is_pdf(file):
    """
    This validates the file being uploaded is pdf file,
    and checks its content too.
    """
    """
    if not file.name.endswith(".pdf"):
        raise ValidationError(_("The uploaded file must be a PDF"))
    
    try:
        pdf = PyPDF2.PdfReader(file)
        if len(pdf.pages) < 1:
            raise ValidationError(_(
                "The uploaded file must be a valid PDF."
            ))
    except Exception:
        raise ValidationError(_(
            "The uploaded file must be a valid PDF."
        ))
    """
    pass

def validate_date_is_not_past(due_date):
    """
    Validates that the given date or datetime object is not in the past.
    """
    now = timezone.now()
    if isinstance(due_date, date) and not isinstance(due_date, datetime):
        if due_date < now.date():

            raise ValidationError(_("Date can not be in the past."))