def format_rupee(value, decimals=False):
    """Return a string formatted as Indian rupee.

    Example:
        1362 -> "₹1,362"
        61589682 -> "₹61,589,682"
        1362.27 -> "₹1,362.27" (if decimals=True or has fraction)
    """
    if value is None:
        return "₹0"
    try:
        num = float(value)
    except (TypeError, ValueError):
        return f"₹{value}"
    
    if decimals:
        return f"₹{num:,.2f}"
    if num.is_integer():
        return f"₹{int(num):,}"
    else:
        return f"₹{num:,.2f}"


def format_number(value):
    """Format regular number with comma separators."""
    if value is None:
        return "0"
    try:
        num = float(value)
        if num.is_integer():
            return f"{int(num):,}"
        return f"{num:,.2f}"
    except (TypeError, ValueError):
        return str(value)
