from django.forms.models import BaseInlineFormSet


class RequiredModelFormSet(BaseInlineFormSet):
    """
    Forces model form set to have atleast one entry
    """
    def __init__(self, *args, **kwargs):
        super(RequiredModelFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
