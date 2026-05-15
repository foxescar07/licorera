from django import template

register = template.Library()


@register.filter(name='pesos')
def pesos(value):
    try:
        n = int(round(float(value)))
        return f"{n:,}".replace(",", ".")
    except (TypeError, ValueError):
        return value