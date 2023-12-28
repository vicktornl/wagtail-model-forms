import json
from collections import OrderedDict

from django import forms
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import conditional_escape
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.forms.forms import FormBuilder as BaseFormBuilder
from wagtail.contrib.forms.models import (
    AbstractFormField as WagtailAbstractFormField,
)
from wagtail.contrib.forms.models import (
    AbstractFormSubmission as WagtailAbstractFormSubmission,
)

from wagtail_model_forms import get_submission_model
from wagtail_model_forms.blocks import FIELDBLOCKS


class AbstractFormSubmission(WagtailAbstractFormSubmission):
    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Page"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.form)


class AbstractFormField(WagtailAbstractFormField):
    class Meta:
        abstract = True


class FormBuilder(BaseFormBuilder):
    def create_singleline_field(self, field, options):
        # TODO: This is a default value - it may need to be changed
        options["max_length"] = 255
        return forms.CharField(
            widget=forms.TextInput(attrs={"placeholder": field["placeholder"]}),
            **options
        )

    def create_multiline_field(self, field, options):
        return forms.CharField(
            widget=forms.Textarea(attrs={"placeholder": field["placeholder"]}),
            **options
        )

    def create_date_field(self, field, options):
        return forms.DateField(
            widget=forms.DateInput(attrs={"placeholder": field["placeholder"]}),
            **options
        )

    def create_datetime_field(self, field, options):
        return forms.DateTimeField(
            widget=forms.DateTimeInput(attrs={"placeholder": field["placeholder"]}),
            **options
        )

    def create_email_field(self, field, options):
        return forms.EmailField(
            widget=forms.EmailInput(attrs={"placeholder": field["placeholder"]}),
            **options
        )

    def create_url_field(self, field, options):
        return forms.URLField(
            widget=forms.URLInput(attrs={"placeholder": field["placeholder"]}),
            **options
        )

    def create_number_field(self, field, options):
        return forms.DecimalField(
            widget=forms.NumberInput(attrs={"placeholder": field["placeholder"]}),
            **options
        )

    def create_file_field(self, field, options):
        return forms.FileField(**options)

    def handle_fieldset(self, structvalue, formfields):
        fieldset = structvalue.value
        fieldset_legend = fieldset["legend"]
        fieldset_label = fieldset["label"]
        for structvalue in fieldset["fields"]:
            field_type = str(structvalue.block_type)
            if field_type == "fieldrow":
                self.handle_fieldrow_in_fieldset(
                    structvalue, formfields, fieldset_label, fieldset_legend
                )
            else:
                self.handle_fieldset_field(
                    structvalue, formfields, fieldset_legend, fieldset_label
                )

    def handle_fieldrow(self, structvalue, formfields):
        fieldrow = structvalue.value
        fieldrow_label = fieldrow["label"]
        for structvalue in fieldrow["fields"]:
            self.handle_fieldrow_field(structvalue, formfields, fieldrow_label)

    def handle_normal_field(self, structvalue, formfields):
        field = structvalue.value
        options = self.get_field_options(field)
        create_field = self.get_create_field_function(str(structvalue.block_type))
        clean_name = field["label"]
        formfields[clean_name] = create_field(field, options)

    def handle_fieldset_field(
        self, structvalue, formfields, fieldset_legend, fieldset_label
    ):
        field = structvalue.value
        options = self.get_field_options(field)
        create_field = self.get_create_field_function(str(structvalue.block_type))
        clean_name = field["label"]
        formfields[clean_name] = create_field(field, options)
        formfields[clean_name].fieldset_legend = fieldset_legend
        formfields[clean_name].fieldset_label = fieldset_label

    def handle_fieldrow_field(self, structvalue, formfields, fieldrow_label):
        field = structvalue.value
        options = self.get_field_options(field)
        create_field = self.get_create_field_function(str(structvalue.block_type))
        clean_name = field["label"]
        formfields[clean_name] = create_field(field, options)
        formfields[clean_name].fieldrow_label = fieldrow_label

    def handle_fieldrow_in_fieldset(
        self, structvalue, formfields, fieldset_label, fieldset_legend
    ):
        fieldrow = structvalue.value
        fieldrow_label = fieldrow["label"]
        clean_name = fieldrow["label"]
        for structvalue in fieldrow["fields"]:
            self.handle_fieldrow_field(structvalue, formfields, fieldrow_label)
            formfields[clean_name].fieldset_legend = fieldset_legend
            formfields[clean_name].fieldset_label = fieldset_label

    @property
    def formfields(self):
        formfields = OrderedDict()

        for structvalue in self.fields:
            field_type = str(structvalue.block_type)
            if field_type == "fieldset":
                self.handle_fieldset(structvalue, formfields)
            elif field_type == "fieldrow":
                self.handle_fieldrow(structvalue, formfields)
            else:
                self.handle_normal_field(structvalue, formfields)
        return formfields

    def get_field_options(self, field):
        options = {"label": field["label"]}
        if getattr(settings, "WAGTAILFORMS_HELP_TEXT_ALLOW_HTML", False):
            options["help_text"] = field["help_text"]
        else:
            options["help_text"] = conditional_escape(field["help_text"])
        options["required"] = field["required"]
        if "default_value" in field:
            options["initial"] = field["default_value"]
        return options

    def get_formatted_field_choices(self, field):
        """
        Returns a list of choices [(string, string),] for the field.
        Split the provided choices into a list, separated by new lines.
        If no new lines in the provided choices, split by commas.
        """

        choices = []
        for choice in field["choices"]:
            choices.append((choice["value"], choice["value"]))
        return choices

    def get_formatted_field_initial(self, field):
        """
        Returns a list of initial values [string,] for the field.
        Split the supplied default values into a list, separated by new lines.
        If no new lines in the provided default values, split by commas.
        """
        if "default_value" in field:
            values = [x.strip() for x in field["default_value"].split(",")]

        return values


class AbstractForm(ClusterableModel):
    title = models.CharField(
        verbose_name=_("title"),
        max_length=255,
    )

    form_builder = FormBuilder

    fields = FIELDBLOCKS

    form_panels = [
        FieldPanel("title", classname="full"),
        FieldPanel("fields"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(form_panels, heading=_("Form")),
        ]
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    @cached_property
    def edit_url(self):
        return None

    def get_form_fields(self):
        form_fields = self.fields
        return form_fields

    def get_data_fields(self):
        data_fields = [
            ("submit_time", _("Submission date")),
        ]
        data_fields += [
            (field.clean_name, field.label) for field in self.get_form_fields()
        ]
        return data_fields

    def get_form_class(self):
        fb = self.form_builder(self.get_form_fields())
        return fb.get_form_class()

    def get_form_parameters(self):
        return {}

    def get_form(self, *args, **kwargs):
        form_class = self.get_form_class()
        form_params = self.get_form_parameters()
        return form_class(*args, **form_params)

    def get_submission_class(self):
        return get_submission_model()

    def process_form_submission(self, form, page=None):
        form_data = json.dumps(form.cleaned_data, cls=DjangoJSONEncoder)
        site = page.get_site()
        form_submission = self.get_submission_class().objects.create(
            form_data=form_data, form=self, page=page
        )
        form_submission.save()
        return form_submission
