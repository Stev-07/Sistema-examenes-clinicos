from django import template

register = template.Library()

#Este metodo sirve para hacer filtros en la plantilla base para manejar el navbar
#segun el grupo al que pertenezca el user porque django no admite filtros como argumentos en la plantilla

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()