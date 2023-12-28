from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail_model_forms.settings import FORM_MODEL


class AbstractFormFieldBlock(blocks.StructBlock):
    label = blocks.CharBlock(label=_("label"))
    help_text = blocks.CharBlock(required=False)
    required = blocks.BooleanBlock(default=True, required=False)

    class Meta:
        abstract = True


class ChoiceBlock(blocks.StructBlock):
    value = blocks.CharBlock()


class PlaceholderMixin(blocks.StructBlock):
    placeholder = blocks.CharBlock(required=False)


class DefaultValueMixin(blocks.StructBlock):
    default_value = blocks.CharBlock(
        required=False,
        help_text=_(
            "Comma separated values, should be the value of a choice or the label of a field"
        ),
    )


class ChoicesMixin(blocks.StructBlock):
    choices = blocks.ListBlock(ChoiceBlock())


class SingleLineTextFieldBlock(
    PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock
):
    class Meta:
        icon = "pilcrow"


class MultipleLineTextFieldBlock(
    PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock
):
    class Meta:
        icon = "pilcrow"


class EmailFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "mail"


class URLFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "site"


class NumberFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "plus-inverse"


class DateFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "date"


class DateTimeFieldBlock(PlaceholderMixin, DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "time"


class DropdownFieldBlock(DefaultValueMixin, ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "arrow-down"


class RadioFieldBlock(DefaultValueMixin, ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "radio-full"


class CheckboxFieldBlock(DefaultValueMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "tick-inverse"


class CheckboxesFieldBlock(DefaultValueMixin, ChoicesMixin, AbstractFormFieldBlock):
    default_value = blocks.CharBlock(
        required=False, help_text=_("Comma separated values")
    )

    class Meta:
        icon = "tick-inverse"


class FileFieldBlock(AbstractFormFieldBlock):
    class Meta:
        icon = "doc-empty-inverse"


class HiddenFieldBlock(AbstractFormFieldBlock):
    class Meta:
        icon = "form"


class MultipleSelectFieldBlock(DefaultValueMixin, ChoicesMixin, AbstractFormFieldBlock):
    class Meta:
        icon = "list-ul"


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
    ("file", FileFieldBlock()),
    ("hidden", HiddenFieldBlock()),
    ("multiselect", MultipleSelectFieldBlock()),
]

COMMON_FIELDBLOCKS = TEXT_INPUT_FIELDBLOCKS + CHOICE_FIELDBLOCKS + UTILITY_FIELDBLOCKS


class FieldRowBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=False)
    fields = blocks.StreamBlock(
        COMMON_FIELDBLOCKS,
        icon="form",
        use_json_field=True,
    )

    class Meta:
        icon = "form"


class FieldSetBlock(blocks.StructBlock):
    legend = blocks.CharBlock(required=False)
    label = blocks.CharBlock(required=False)
    fields = blocks.StreamBlock(
        COMMON_FIELDBLOCKS + [("fieldrow", FieldRowBlock())],
        icon="form",
        use_json_field=True,
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
        ("file", FileFieldBlock()),
        ("hidden", HiddenFieldBlock()),
        ("multiselect", MultipleSelectFieldBlock()),
        ("fieldset", FieldSetBlock()),
        ("fieldrow", FieldRowBlock()),
    ],
    blank=True,
    null=True,
    verbose_name="Fields",
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
