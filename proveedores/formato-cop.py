from django import template
from decimal import Decimal

register = template.Library()

@register.filter(name='cop')
def cop(value):
    try:
        n = int(Decimal(str(value)))
        resultado = '{:,}'.format(n).replace(',', '.')
        return resultado
    except:
        return value