"""
Currency conversion utilities for Bulgarian car service system
Handles BGN to EUR conversion and dual currency display
"""

from decimal import Decimal, ROUND_HALF_UP
from django.core.cache import cache
from datetime import datetime, timedelta


def get_eur_rate():
    """
    Get current EUR to BGN exchange rate
    For now, uses a fixed rate. In production, this would fetch from BNB API
    """
    # Try to get from cache first (cache for 1 hour)
    cached_rate = cache.get('eur_bgn_rate')
    if cached_rate:
        return Decimal(str(cached_rate))
    
    # For now, use a fixed rate (update this regularly)
    # In production, you would fetch from Bulgarian National Bank API
    fallback_rate = Decimal('1.95583')  # Approximate BGN/EUR rate
    cache.set('eur_bgn_rate', float(fallback_rate), 3600)
    return fallback_rate


def bgn_to_eur(bgn_amount):
    """
    Convert BGN amount to EUR
    """
    if not bgn_amount:
        return Decimal('0.00')
    
    bgn_decimal = Decimal(str(bgn_amount))
    eur_rate = get_eur_rate()
    eur_amount = bgn_decimal / eur_rate
    return eur_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def eur_to_bgn(eur_amount):
    """
    Convert EUR amount to BGN
    """
    if not eur_amount:
        return Decimal('0.00')
    
    eur_decimal = Decimal(str(eur_amount))
    eur_rate = get_eur_rate()
    bgn_amount = eur_decimal * eur_rate
    return bgn_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def format_dual_currency(bgn_amount, show_eur=True):
    """
    Format amount in both BGN and EUR
    Returns formatted string like "100.00 лв. (51.15 €)"
    """
    if not bgn_amount:
        return "0.00 лв."
    
    bgn_decimal = Decimal(str(bgn_amount))
    bgn_formatted = f"{bgn_decimal:.2f} лв."
    
    if show_eur:
        eur_amount = bgn_to_eur(bgn_decimal)
        eur_formatted = f"{eur_amount:.2f} €"
        return f"{bgn_formatted} ({eur_formatted})"
    
    return bgn_formatted


def format_currency_table(bgn_amount, show_eur=True):
    """
    Format amount for table display with separate BGN and EUR columns
    Returns tuple: (bgn_formatted, eur_formatted)
    """
    if not bgn_amount:
        return ("0.00 лв.", "0.00 €")
    
    bgn_decimal = Decimal(str(bgn_amount))
    bgn_formatted = f"{bgn_decimal:.2f} лв."
    
    if show_eur:
        eur_amount = bgn_to_eur(bgn_decimal)
        eur_formatted = f"{eur_amount:.2f} €"
        return (bgn_formatted, eur_formatted)
    
    return (bgn_formatted, "")


def get_currency_info():
    """
    Get current currency information
    Returns dict with rate and last updated info
    """
    rate = get_eur_rate()
    return {
        'eur_rate': float(rate),
        'last_updated': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'rate_text': f"1 EUR = {rate:.5f} BGN"
    }
