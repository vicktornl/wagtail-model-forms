from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, Fieldset, Layout, Row


# Add this mixin to you AbstractForm to use crispy forms, with fieldsets and rows.
# DISCLAIMER: U need to load the formtag like this {% crispy form form.helper %} and not like this form|crispy or the form will not be rendered correctly.
class CrispyFormLayoutMixin:
    def get_form_layout(self):
        layout = []
        for structvalue in self.fields:
            field_type = str(structvalue.block_type)
            if field_type == "fieldset":
                layout.append(self.handle_fieldset_layout(structvalue))
            elif field_type == "fieldrow":
                layout.append(Row(*self.handle_fieldrow_layout(structvalue)))
            else:
                field_name = structvalue.value["label"]
                layout.append(Field(field_name))
        return Layout(*layout)

    def handle_fieldset_layout(self, structvalue):
        fieldset = structvalue.value
        layout_fields = []
        for structvalue in fieldset["form_fields"]:
            field_type = str(structvalue.block_type)
            if field_type == "fieldrow":
                layout_fields.append(Row(*self.handle_fieldrow_layout(structvalue)))
            else:
                field_name = structvalue.value["label"]
                layout_fields.append(Field(field_name))
        return Fieldset(fieldset["legend"], *layout_fields)

    def handle_fieldrow_layout(self, structvalue):
        fieldrow = structvalue.value
        layout_fields = []
        for structvalue in fieldrow["form_fields"]:
            field_name = structvalue.value["label"]
            col_int = 12 // len(fieldrow["form_fields"])
            col_class = "col-" + str(col_int)
            layout_fields.append(Div(Field(field_name), css_class=col_class))
        return layout_fields

    def get_form_helper(self):
        helper = FormHelper()
        helper.layout = self.get_form_layout()
        return helper

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        form_params = self.get_form_parameters()
        form = form_class(*args, **form_params)
        form.helper = self.get_form_helper()
        return form
