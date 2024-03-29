from django import template
from rango.models import Category
from booktime.models import ProductTag

register = template.Library()


@register.inclusion_tag('rango/cats.html')
def get_category_list(cat=None):
    return {'cats': Category.objects.all(), 'act_cat': cat}


@register.inclusion_tag('tags.html')
def get_tags_list(tag=None):
    return {'tags': ProductTag.objects.all(), 'act_tag': tag}