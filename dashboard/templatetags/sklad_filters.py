from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def smart_quantity(value):
    """
    Display quantity as integer if it's a round number, otherwise show with 2 decimal places
    """
    if value is None:
        return "0"
    
    # Convert to float first
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    # Check if it's a whole number
    if float_value == int(float_value):
        return str(int(float_value))
    else:
        return f"{float_value:.2f}"

@register.filter
def add_class(field, css_class):
    """Add CSS class to form field"""
    return field.as_widget(attrs={'class': css_class})

@register.filter
def add_attr(field, attr_string):
    """Add attribute to form field"""
    if ':' in attr_string:
        key, value = attr_string.split(':', 1)
        return field.as_widget(attrs={key: value})
    return field

@register.filter
def add_class_and_attrs(field, attrs_string):
    """Add CSS class and multiple attributes to form field"""
    attrs = {}
    
    # Split by | to get individual attributes
    attr_pairs = attrs_string.split('|')
    
    for attr_pair in attr_pairs:
        if ':' in attr_pair:
            key, value = attr_pair.split(':', 1)
            if key == 'class':
                # Handle class specially - merge with existing classes
                if 'class' in attrs:
                    attrs['class'] = f"{attrs['class']} {value}"
                else:
                    attrs['class'] = value
            else:
                attrs[key] = value
    
    return field.as_widget(attrs=attrs)

@register.filter
def mul(value, arg):
    """Multiply two values"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
