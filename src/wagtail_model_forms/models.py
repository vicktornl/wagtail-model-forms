import json
from collections import OrderedDict

from django import forms
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import conditional_escape
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, ObjectList, TabbedInterface
from wagtail.contrib.forms.forms import FormBuilder as BaseFormBuilder
from wagtail.contrib.forms.models import (
    AbstractFormField as WagtailAbstractFormField,
)
from wagtail.contrib.forms.models import (
    AbstractFormSubmission as WagtailAbstractFormSubmission,
)

from wagtail_model_forms import get_submission_model
from wagtail_model_forms.blocks import FIELDBLOCKS


def get_field_clean_name(field_value, namespace=""):
    if namespace:
        return "{}.{}".format(namespace, slugify(field_value["label"]))
    else:
        return slugify(field_value["label"])


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

    def create_dropdown_field(self, field, options):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.ChoiceField(**options)

    def create_multiselect_field(self, field, options):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.MultipleChoiceField(**options)

    def create_radio_field(self, field, options):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.ChoiceField(widget=forms.RadioSelect, **options)

    def create_checkboxes_field(self, field, options):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, **options)

    def handle_normal_field(self, structvalue, formfields, namespace=""):
        field = structvalue.value
        options = self.get_field_options(field)
        create_field = self.get_create_field_function(str(structvalue.block_type))
        clean_name = get_field_clean_name(field, namespace)

        formfields[clean_name] = create_field(field, options)

    def handle_fieldset(self, structvalue, formfields, namespace=""):
        fieldset = structvalue.value
        for structvalue in fieldset["form_fields"]:
            field_type = str(structvalue.block_type)
            if field_type == "fieldrow":
                self.handle_fieldrow(structvalue, formfields, namespace=namespace)
            else:
                self.handle_normal_field(structvalue, formfields, namespace=namespace)

    def handle_fieldrow(self, structvalue, formfields, namespace=""):
        fieldrow = structvalue.value
        for structvalue in fieldrow["form_fields"]:
            self.handle_normal_field(structvalue, formfields, namespace=namespace)

    @property
    def formfields(self):
        """
        Returns an OrderedDict of form fields.
        """
        formfields = OrderedDict()

        for structvalue in self.fields:
            field_type = str(structvalue.block_type)
            if field_type == "fieldset":
                namespace = slugify(structvalue.value["legend"])
                self.handle_fieldset(structvalue, formfields, namespace)
            elif field_type == "fieldrow":
                self.handle_fieldrow(structvalue, formfields)
            else:
                self.handle_normal_field(structvalue, formfields, namespace="")
        return formfields

    def get_field_options(self, field):
        """
        Returns a dictionary of options for the field.
        """
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
        """
        choices = []
        for choice in field["choices"]:
            choices.append((choice["value"], choice["value"]))
        return choices

    def get_formatted_field_initial(self, field):
        """
        Returns a list of initial values [string,] for the field.
        """
        values = []
        for choice in field["choices"]:
            if choice["default_value"] == True:
                values.append(choice["value"])
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
        return self.fields

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

    def get_form_data(self, form, request=None):
        form_data = form.cleaned_data
        return form_data

    def process_form_submission(self, form, page=None, request=None):
        form_data = json.dumps(
            self.get_form_data(form, request=request), cls=DjangoJSONEncoder
        )
        site = page.get_site()
        form_submission = self.get_submission_class().objects.create(
            form_data=form_data, form=self, page=page
        )
        form_submission.save()
        return form_submission
