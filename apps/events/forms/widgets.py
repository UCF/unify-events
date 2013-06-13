from django import forms
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe


class InlineLDAPSearch(forms.Widget):

    def render(self, name, value, attrs=None):

        html = list()
        html.append('<div class="inlineldapsearch clearfix">')
        html.append('<div class="input"><input type="text" class="query" />')
        html.append('<button class="search">Search</button></div>')
        html.append('<select multiple="multiple" class="choices" size="5"></select>')
        html.append('<ul class="actions"><li><a class="add">Add</a></li>')
        html.append('<li><a class="remove">Remove</a></li></ul>')
        html.append('<select multiple="multiple" class="selections" name="%s">' % name)
        if value is not None:
            for user_id in value:
                user = User.objects.get(pk=user_id)
                display = user.first_name + ' ' + user.last_name + ' (' + user.username + ')'
                html.append('<option value="%d">%s</option>' % (user_id, display))
        html.append('</select></div>')
        return mark_safe(u'\n'.join(html))