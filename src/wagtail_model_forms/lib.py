from cProfile import label
from turtle import title

from httpx import stream
from wagtail.blocks import StreamValue, StructValue

from wagtail_model_forms.blocks import (
    CheckboxesFieldBlock,
    CheckboxFieldBlock,
    DateFieldBlock,
    DateTimeFieldBlock,
    DropdownFieldBlock,
    EmailFieldBlock,
    HiddenFieldBlock,
    MultipleLineTextFieldBlock,
    MultipleSelectFieldBlock,
    NumberFieldBlock,
    RadioFieldBlock,
    SingleLineTextFieldBlock,
    URLFieldBlock,
)
from wagtail_model_forms.models import AbstractForm, AbstractFormField

"""
form.fields should look like:
<StreamValue [<block fieldset: StructValue([('legend', 'fieldset legend'), ('form_fields', <StreamValue [<block singleline: StructValue([('label', 'inside a fieldset'), ('help_text', ''), ('required', True), ('default_value', ''), ('placeholder', '')])>, <block singleline: StructValue([('label', 'inside a fieldset2'), ('help_text', ''), ('required', True), ('default_value', ''), ('placeholder', '')])>]>)])>, <block datetime: StructValue([('label', 'sdffsd'), ('help_text', ''), ('required', True), ('default_value', datetime.datetime(2024, 1, 12, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)))), ('placeholder', datetime.datetime(2024, 1, 11, 14, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))))])>, <block fieldrow: StructValue([('form_fields', <StreamValue [<block checkbox: StructValue([('label', 'iohopuh'), ('help_text', ''), ('required', False), ('default_value', False)])>]>)])>, <block checkboxes: StructValue([('label', 'labeltje'), ('help_text', 'help checkboxes'), ('required', True), ('choices', <ListValue: [StructValue([('value', 'value1'), ('default_value', True)]), StructValue([('value', 'value2'), ('default_value', True)])]>)])>, <block checkbox: StructValue([('label', 'dsfsdf'), ('help_text', 'sdfsdf'), ('required', True), ('default_value', True)])>, <block radio: StructValue([('label', 'adsad'), ('help_text', 'asdasdasd'), ('required', True), ('choices', <ListValue: [StructValue([('value', 'value3'), ('default_value', False)]), StructValue([('value', 'value5'), ('default_value', False)])]>)])>, <block multiselect: StructValue([('label', 'label'), ('help_text', 'help'), ('required', True), ('choices', <ListValue: [StructValue([('value', 'val1'), ('default_value', False)]), StructValue([('value', 'val2'), ('default_value', False)]), StructValue([('value', 'val3'), ('default_value', False)])]>)])>, <block dropdown: StructValue([('label', 'dropdowntje'), ('help_text', 'help tetx'), ('required', True), ('choices', <ListValue: [StructValue([('value', 'value1'), ('default_value', False)]), StructValue([('value', 'choice2'), ('default_value', False)]), StructValue([('value', 'choice3'), ('default_value', False)])]>)])>, <block number: StructValue([('label', 'numberlabel'), ('help_text', 'number help'), ('required', True), ('default_value', 3), ('placeholder', None)])>, <block date: StructValue([('label', 'date'), ('help_text', 'datehelp'), ('required', True), ('default_value', None), ('placeholder', datetime.date(2024, 1, 10))])>]>
"""


def migrate_old_form(form_instance, form_model):
    new_fields = []
    for field in form_instance.form_fields.all():
        if field.field_type == "singleline":
            field_type = "singleline"
            new_field = StructValue(
                SingleLineTextFieldBlock(),
                [
                    ("label", field.label),
                    ("help_text", field.help_text),
                    ("required", field.required),
                    ("default_value", field.default_value),
                    ("placeholder", ""),
                ],
            )
            new_fields.append(new_field)
