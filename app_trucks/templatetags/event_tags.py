from django import template
from ..models import Company
from datetime import datetime, date

register = template.Library()


@register.filter(name='company_verbose')
def company_verbose(_id):
    company = Company.objects.get(pk=_id)
    return str(company)


@register.filter(name='weekday_spanish')
def weekday_spanish(_date):

    weekday_choices = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']

    weekday_as_number = _date.weekday()

    return weekday_choices[weekday_as_number]


@register.filter(name='days_ago')
def days_ago(_date):

    delta = datetime.now().date() - _date

    if delta.days == 0:
        return 'Hoy'

    elif delta.days == 1:
        return 'Ayer'

    else:
        return str(delta.days) + ' días'
