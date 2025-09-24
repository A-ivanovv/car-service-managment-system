"""
Template filters for currency formatting
"""

from django import template
from django.utils.safestring import mark_safe
from ..currency_utils import format_dual_currency, format_currency_table, get_currency_info

register = template.Library()


@register.filter
def dual_currency(value, show_eur=True):
    """
    Format value in both BGN and EUR
    Usage: {{ value|dual_currency }}
    """
    if value is None:
        return "0.00 лв."
    return format_dual_currency(value, show_eur)


@register.filter
def currency_bgn(value):
    """
    Format value in BGN only
    Usage: {{ value|currency_bgn }}
    """
    if value is None:
        return "0.00 лв."
    return f"{value:.2f} лв."


@register.filter
def currency_eur(value):
    """
    Format value in EUR only
    Usage: {{ value|currency_eur }}
    """
    if value is None:
        return "0.00 €"
    from ..currency_utils import bgn_to_eur
    eur_value = bgn_to_eur(value)
    return f"{eur_value:.2f} €"


@register.filter
def currency_table(value):
    """
    Format value for table display with separate BGN and EUR columns
    Usage: {{ value|currency_table }}
    Returns tuple: (bgn_formatted, eur_formatted)
    """
    if value is None:
        return ("0.00 лв.", "0.00 €")
    return format_currency_table(value, True)


@register.simple_tag
def currency_info():
    """
    Get current currency information
    Usage: {% currency_info %}
    """
    info = get_currency_info()
    return mark_safe(f"<small class='text-muted'>{info['rate_text']} (обновено: {info['last_updated']})</small>")


@register.simple_tag
def eur_rate():
    """
    Get current EUR rate
    Usage: {% eur_rate %}
    """
    info = get_currency_info()
    return info['eur_rate']
