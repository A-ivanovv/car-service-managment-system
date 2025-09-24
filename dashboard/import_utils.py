import re
from datetime import datetime
from typing import Optional, Tuple


def extract_invoice_number_from_starts94(content: str) -> Optional[str]:
    """
    Extract invoice number from Стартс94 format:
    'Приемо-предавателен протокол за даване на стокa № SR000731088'
    """
    pattern = r'Приемо-предавателен протокол за даване на стокa №\s*([A-Z0-9]+)'
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1) if match else None


def extract_invoice_number_from_peugeot(content: str) -> Optional[str]:
    """
    Extract invoice number from Peugeot format:
    'ФАКТУРА No: 0070139042'
    """
    pattern = r'ФАКТУРА\s+No:\s*([0-9]+)'
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1) if match else None


def extract_date_from_xls(content: str) -> Optional[str]:
    """
    Extract date from XLS format:
    'Към дата 04/09/2025'
    """
    pattern = r'Към дата\s+(\d{2}/\d{2}/\d{4})'
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1) if match else None


def generate_import_identifier(provider: str, invoice_number: str = None, invoice_date: str = None) -> str:
    """
    Generate a unique import identifier based on provider and invoice details
    """
    if provider == 'starts94' and invoice_number:
        return f"starts94_{invoice_number}"
    elif provider == 'peugeot' and invoice_number:
        return f"peugeot_{invoice_number}"
    elif provider == 'nalichnosti' and invoice_date:
        return f"nalichnosti_{invoice_date}"
    else:
        # Fallback to timestamp
        return f"{provider}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def extract_invoice_info(content: str, provider: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract invoice number and date from content based on provider
    Returns: (invoice_number, invoice_date)
    """
    invoice_number = None
    invoice_date = None
    
    if provider == 'starts94':
        invoice_number = extract_invoice_number_from_starts94(content)
    elif provider == 'peugeot':
        invoice_number = extract_invoice_number_from_peugeot(content)
    elif provider == 'nalichnosti':
        invoice_date = extract_date_from_xls(content)
    
    return invoice_number, invoice_date


def check_duplicate_import(provider: str, invoice_number: str = None, invoice_date: str = None) -> bool:
    """
    Check if an import with the same identifier already exists
    """
    from .models import ImportLog
    
    identifier = generate_import_identifier(provider, invoice_number, invoice_date)
    return ImportLog.objects.filter(import_identifier=identifier).exists()


def get_duplicate_import_info(provider: str, invoice_number: str = None, invoice_date: str = None) -> Optional[dict]:
    """
    Get information about duplicate import if it exists
    """
    from .models import ImportLog
    
    identifier = generate_import_identifier(provider, invoice_number, invoice_date)
    try:
        duplicate = ImportLog.objects.get(import_identifier=identifier)
        return {
            'exists': True,
            'import_date': duplicate.import_date,
            'file_name': duplicate.file_name,
            'invoice_number': duplicate.invoice_number,
            'invoice_date': duplicate.invoice_date,
            'provider': duplicate.get_provider_display(),
        }
    except ImportLog.DoesNotExist:
        return None
