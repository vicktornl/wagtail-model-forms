from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail_model_forms.settings import FORM_MODEL


class AbstractFormFieldBlock(blocks.StructBlock):
    label = blocks.CharBlock(
        label=_("Label"),
    )
    help_text = blocks.CharBlock(
        required=False,
        label=_("Help text"),
    )
    required = blocks.BooleanBlock(
        default=True,
        required=False,
        label=_("Required"),
        help_text=_("Check this box if this field is required to be filled in"),
    )

    class Meta:
        abstract = True


class ChoiceBlock(blocks.StructBlock):
    value = blocks.CharBlock(label=_("Choice"))
    default_value = blocks.BooleanBlock(
        required=False,
        label=_("Checked by default"),
        help_text=_("Check this box if you want this to be checked by default"),
    )


class PlaceholderMixin(blocks.StructBlock):
    placeholder = blocks.CharBlock(
        required=False,
        label=_("Placeholder"),
    )


class DateMixin(blocks.StructBlock):
    default_value = blocks.DateBlock(
        required=False,
        label=_("Default value"),
    )
    placeholder = blocks.DateBlock(
        required=False,
        label=_("Placeholder"),
    )


class DefaultValueMixin(blocks.StructBlock):
    default_value = blocks.CharBlock(
        required=False,
        label=_("Default value"),
    )


class ChoicesMixin(blocks.StructBlock):
    choices = blocks.ListBlock(
        ChoiceBlock(),
        label=_("Choices"),
    )


class SingleLineTextFieldBlock(
    PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock
):
    class Meta:
        icon = "pilcrow"
        label = _("Singleline text")


class MultipleLineTextFieldBlock(
    PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock
):
    class Meta:
        icon = "pilcrow"
        label = _("Multiline text")


class EmailFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "mail"
        label = _("Email")


class URLFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "site"
        label = _("URL")


class NumberFieldBlock(AbstractFormFieldBlock):
    default_value = blocks.IntegerBlock(
        required=False,
        label=_("Default value"),
    )
    placeholder = blocks.IntegerBlock(
        required=False,
        label=_("Placeholder"),
    )

    class Meta:
        icon = "plus-inverse"
        label = _("Number")


class DateFieldBlock(AbstractFormFieldBlock):
    default_value = blocks.DateBlock(
        required=False,
        label=_("Default value"),
    )
    placeholder = blocks.DateBlock(
        required=False,
        label=_("Placeholder"),
    )

    class Meta:
        icon = "date"
        label = _("Date")


class DateTimeFieldBlock(AbstractFormFieldBlock):
    default_value = blocks.DateTimeBlock(
        required=False,
        label=_("Default value"),
    )
    placeholder = blocks.DateTimeBlock(
        required=False,
        label=_("Placeholder"),
    )

    class Meta:
        icon = "time"
        label = _("Date and time")


class DropdownFieldBlock(ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "arrow-down"
        label = _("Dropdown")


class RadioFieldBlock(ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "radio-full"
        label = _("Radio group")


class CheckboxFieldBlock(AbstractFormFieldBlock):
    default_value = blocks.BooleanBlock(
        required=False,
        label=_("Checked by default"),
    )

    class Meta:
        icon = "tick-inverse"
        label = _("Checkbox")


class CheckboxesFieldBlock(ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "tick-inverse"
        label = _("Checkboxes")


class HiddenFieldBlock(AbstractFormFieldBlock):
    class Meta:
        icon = "form"


class MultipleSelectFieldBlock(ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "list-ul"
        label = _("Multiselect")


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
    )

    class Meta:
        icon = "form"


class FieldSetBlock(blocks.StructBlock):
    legend = blocks.CharBlock(
        label=_("Legend"),
    )
    form_fields = blocks.StreamBlock(
        [("fieldrow", FieldRowBlock())] + COMMON_FIELDBLOCKS,
        icon="form",
        use_json_field=True,
        verbose_name=_("Form fields"),
    )

    class Meta:
        icon = "list-ul"


FIELDBLOCKS = StreamField(
    [
        ("fieldset", FieldSetBlock()),
        ("fieldrow", FieldRowBlock()),
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
        ("multiselect", MultipleSelectFieldBlock()),
        ("hidden", HiddenFieldBlock()),
    ],
    blank=True,
    null=True,
    verbose_name=_("Form fields"),
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
