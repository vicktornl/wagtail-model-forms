from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail_model_forms.settings import FORM_MODEL


class AbstractFormFieldBlock(blocks.StructBlock):
    label = blocks.CharBlock(label=_("Label"), help_text=_("The label of the form field."))
    help_text = blocks.CharBlock(required=False, label=_("Help Text"), help_text=_("Optional help text for the form field. Will be displayed below the field."))
    required = blocks.BooleanBlock(default=True, required=False, label=_("Required"), help_text=_("Check this box if the field is required to be filled in."))

    class Meta:
        abstract = True

class ChoiceBlock(blocks.StructBlock):
    value = blocks.CharBlock(label=_("Choice"), help_text=_("Fill in the choice here."))
    default_value = blocks.BooleanBlock(required=False, label=_("Checked by default"), help_text=_("Check this box if u want it to be checked by default."))

class PlaceholderMixin(blocks.StructBlock):
    placeholder = blocks.CharBlock(required=False, label=_("Placeholder"), help_text=_("Placeholder text for the field. will be shown when the field is empty(greyed out)."))

class DefaultValueMixin(blocks.StructBlock):
    default_value = blocks.CharBlock(
        required=False,
        label=_("Default Value"),
        help_text=_("This value will be used as the default(prefilled) value for the field."),
    )

class ChoicesMixin(blocks.StructBlock):
    choices = blocks.ListBlock(ChoiceBlock(), label=_("Choices"), help_text=_("Click here to add more choices for this field."))

class SingleLineTextFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "pilcrow"
        label = _("Single Line Text Field")
        help_text = _("A single line text input field.")

class MultipleLineTextFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "pilcrow"
        label = _("Multiple Line Text Field")
        help_text = _("A multi-line text input field.")

class EmailFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "mail"
        label = _("Email Field")
        help_text = _("An input field for email addresses.")

class URLFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "site"
        label = _("URL Field")
        help_text = _("An input field for URLs.")


class NumberFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "plus-inverse"
        label = _("Number Field")
        help_text = _("An input field for numeric values.")


class DateFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "date"
        label = _("Date Field")
        help_text = _("An input field for dates.")


class DateTimeFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "time"
        label = _("Date / Time Field")
        help_text = _("An input field for dates and times.")


class DropdownFieldBlock(ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "arrow-down"
        label = _("Dropdown Field")
        help_text = _("A dropdown selection field.")


class RadioFieldBlock(ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "radio-full"
        label = _("Radio Field")
        help_text = _("A radio selection field.")


class CheckboxFieldBlock(AbstractFormFieldBlock):
    default_value = blocks.BooleanBlock(required=False)
    class Meta:
        icon = "tick-inverse"
        label = _("Checkbox Field")
        help_text = _("A checkbox selection field.")


class CheckboxesFieldBlock(ChoicesMixin, AbstractFormFieldBlock):

    class Meta:
        icon = "tick-inverse"
        label = _("Checkboxes Field")
        help_text = _("A checkbox selection field.")


class HiddenFieldBlock(AbstractFormFieldBlock):
    class Meta:
        icon = "form"


class MultipleSelectFieldBlock(ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "list-ul"
        label = _("Multiple Select Field")
        help_text = _("A multiple select field.")


# Do not change the given names(strings) of the fieldblocks, these are used for method lookups.
TEXT_INPUT_FIELDBLOCKS = [
    ("singleline", SingleLineTextFieldBlock()),
    ("multiline", MultipleLineTextFieldBlock()),
    ("email", EmailFieldBlock()),
    ("url", URLFieldBlock()),
    ("number", NumberFieldBlock()),
    ("date", DateFieldBlock()),
    ("datetime", DateTimeFieldBlock()),
]

CHOICE_FIELDBLOCKS = [
    ("dropdown", DropdownFieldBlock()),
    ("radio", RadioFieldBlock()),
    ("checkbox", CheckboxFieldBlock()),
    ("checkboxes", CheckboxesFieldBlock()),
]

UTILITY_FIELDBLOCKS = [
    ("hidden", HiddenFieldBlock()),
    ("multiselect", MultipleSelectFieldBlock()),
]

COMMON_FIELDBLOCKS = TEXT_INPUT_FIELDBLOCKS + CHOICE_FIELDBLOCKS + UTILITY_FIELDBLOCKS


class FieldRowBlock(blocks.StructBlock):
    form_fields = blocks.StreamBlock(
        COMMON_FIELDBLOCKS,
        icon="form",
        use_json_field=True,
        verbose_name=_("Form fields"),
        help_text=_("Click to add more fields to your field row"),
    )

    class Meta:
        icon = "form"


class FieldSetBlock(blocks.StructBlock):
    legend = blocks.CharBlock(label=_("Legend"), help_text=_("The legend of the fieldset. accessability purposes."))
    form_fields = blocks.StreamBlock(
        COMMON_FIELDBLOCKS + [("fieldrow", FieldRowBlock())],
        icon="form",
        use_json_field=True,
        verbose_name=_("Form fields"),
        help_text=_("Click to add more fields to your field set"),
    )

    class Meta:
        icon = "list-ul"


# Do not change the given names(strings) of the fieldblocks, these are used for method lookups.
FIELDBLOCKS = StreamField(
    [
        ("singleline", SingleLineTextFieldBlock()),
        ("multiline", MultipleLineTextFieldBlock()),
        ("email", EmailFieldBlock()),
        ("url", URLFieldBlock()),
        ("number", NumberFieldBlock()),
        ("date", DateFieldBlock()),
        ("datetime", DateTimeFieldBlock()),
        ("dropdown", DropdownFieldBlock()),
        ("radio", RadioFieldBlock()),
        ("checkbox", CheckboxFieldBlock()),
        ("checkboxes", CheckboxesFieldBlock()),
        ("hidden", HiddenFieldBlock()),
        ("multiselect", MultipleSelectFieldBlock()),
        ("fieldset", FieldSetBlock()),
        ("fieldrow", FieldRowBlock()),
    ],
    blank=True,
    null=True,
    verbose_name=_("Form fields"),
    help_text=_("Click to add more fields to your form"),
    use_json_field=True,
)


class AbstractFormBlock(blocks.StructBlock):
    form = SnippetChooserBlock(FORM_MODEL)

    class Meta:
        abstract = True

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        page = context["page"]
        request = context["request"]
        user = request.user
        form_obj = context["self"]["form"]

        if request.method == "POST" and "form_id" in request.POST:
            user = request.user

            form = form_obj.get_form(request.POST, request.FILES, page=page, user=user)
            form.is_valid()
        else:
            form = form_obj.get_form(page=page, user=user)

        context["form"] = form
        return context

    class Meta:
        abstract = True


class FormBlock(AbstractFormBlock):
    class Meta:
        icon = "form"
        template = "wagtail_model_forms/form.html"
