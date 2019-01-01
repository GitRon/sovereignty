from django import template

register = template.Library()


@register.simple_tag
def active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'active'
    return ''


@register.filter
def multiply(factor1, factor2):
    return factor1 * factor2
