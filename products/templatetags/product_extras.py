from django import template

register = template.Library()


@register.filter
def star_rating(value):
    """Convert a rating value (e.g. 4.5) to star characters."""
    try:
        rating = float(value)
    except (ValueError, TypeError):
        return ''

    full = int(rating)
    half = 1 if (rating - full) >= 0.25 else 0
    empty = 5 - full - half

    stars = '★' * full + '½' * half + '☆' * empty
    return stars


@register.filter
def format_reviews(count):
    """Format review count like Amazon: 1.2K, 342, etc."""
    try:
        count = int(count)
    except (ValueError, TypeError):
        return '0'

    if count >= 1000:
        return f'{count / 1000:.1f}K'
    return str(count)