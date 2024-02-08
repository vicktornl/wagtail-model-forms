from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Fieldset, Layout, Row

from wagtail_model_forms.settings import CIRSPY_FORMS_FORM_TAG


class CrispyFormLayoutMixin:
    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.helper = self.get_form_helper()
        print(form.helper)
        return form

    def get_form_helper(self):
        helper = FormHelper()
        helper.form_tag = CIRSPY_FORMS_FORM_TAG
        helper.layout = self.get_form_layout()
        return helper

    def get_form_layout(self):
        layout_objects = []
        for field in self.fields:
            layout_objects += self.get_layout_objects_from_field(field)
        layout = Layout(*layout_objects)
        return layout

    def get_layout_objects_from_field(self, field):
        layout_objects = []
        block_type = field.block_type
        if block_type == "fieldset":
            child_objects = []
            for child_field in field.value["form_fields"]:
                child_objects += self.get_layout_objects_from_field(child_field)
            layout_objects.append(Fieldset("Naam van fieldset", *child_objects))
        elif block_type == "fieldrow":
            child_objects = []
            for child_field in field.value["form_fields"]:
                child_objects += self.get_layout_objects_from_field(child_field)
            layout_objects.append(Row(*child_objects))
        else:
            layout_objects.append(Field(field.value["label"]))
        return layout_objects
