import json
import logging
from collections import OrderedDict

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.functional import cached_property
from django.utils.html import conditional_escape
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
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
from wagtail.fields import StreamField

from wagtail_model_forms import get_submission_model, get_uploaded_file_model
from wagtail_model_forms.blocks import FIELDBLOCKS, WebhookBlock
from wagtail_model_forms.settings import FORM_MODEL, SUBMISSION_MODEL
from wagtail_model_forms.utils import trigger_webhook

logger = logging.getLogger(__name__)


def get_field_clean_name(field_value, namespace=""):
    if namespace:
        return "{}.{}".format(namespace, slugify(field_value["label"]))
    else:
        return slugify(field_value["label"])


class AbstractFormSubmission(WagtailAbstractFormSubmission):
    class Status(models.TextChoices):
        NEW = "new", _("New")
        COMPLETED = "completed", _("Completed")

    form = models.ForeignKey(
        "cms.Form",
        on_delete=models.CASCADE,
        related_name="form_submissions",
        verbose_name=_("Form"),
    )
    page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Page"),
    )
    status = models.CharField(
        max_length=255,
        choices=Status,
        default=Status.NEW,
        verbose_name=_("Status"),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.form)


class AbstractUploadedFile(models.Model):
    form_submission = models.ForeignKey(
        SUBMISSION_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_files",
    )
    file = models.FileField()
    created_at = models.DateTimeField(
        verbose_name=_("created at"),
        auto_now_add=True,
    )

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.form_submission)

    @property
    def download_url(self):
        return self.file.url


class AbstractFormField(WagtailAbstractFormField):
    class Meta:
        abstract = True


class FormBuilder(BaseFormBuilder):
    def create_singleline_field(self, field, options, default_widget_attrs={}):
        # TODO: This is a default value - it may need to be changed
        options["max_length"] = 255
        return forms.CharField(
            widget=forms.TextInput(attrs=default_widget_attrs),
            **options
        )

    def create_multiline_field(self, field, options, default_widget_attrs={}):
        return forms.CharField(
            widget=forms.Textarea(attrs=default_widget_attrs),
            **options
        )

    def create_date_field(self, field, options, default_widget_attrs={}):
        return forms.DateField(
            widget=forms.DateInput(attrs=default_widget_attrs),
            **options
        )

    def create_datetime_field(self, field, options, default_widget_attrs={}):
        return forms.DateTimeField(
            widget=forms.DateTimeInput(attrs=default_widget_attrs),
            **options
        )

    def create_email_field(self, field, options, default_widget_attrs={}):
        return forms.EmailField(
            widget=forms.EmailInput(attrs=default_widget_attrs),
            **options
        )

    def create_url_field(self, field, options, default_widget_attrs={}):
        return forms.URLField(
            widget=forms.URLInput(attrs=default_widget_attrs),
            **options
        )

    def create_number_field(self, field, options, default_widget_attrs={}):
        return forms.DecimalField(
            widget=forms.NumberInput(attrs=default_widget_attrs),
            **options
        )

    def create_dropdown_field(self, field, options, default_widget_attrs={}):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.ChoiceField(**options)

    def create_multiselect_field(self, field, options, default_widget_attrs={}):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.MultipleChoiceField(**options)

    def create_radio_field(self, field, options, default_widget_attrs={}):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.ChoiceField(widget=forms.RadioSelect, **options)

    def create_checkbox_field(self, field, options, default_widget_attrs={}):
        return forms.BooleanField(
            widget=forms.CheckboxInput(attrs=default_widget_attrs), **options
        )

    def create_checkboxes_field(self, field, options, default_widget_attrs={}):
        options["choices"] = self.get_formatted_field_choices(field)
        options["initial"] = self.get_formatted_field_initial(field)
        return forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, **options)

    def create_file_field(self, field, options, default_widget_attrs={}):
        return forms.FileField(**options)

    def handle_normal_field(self, structvalue, formfields, namespace=""):
        field = structvalue.value
        options = self.get_field_options(field)
        create_field = self.get_create_field_function(str(structvalue.block_type))
        clean_name = get_field_clean_name(field, namespace)
        default_widget_attrs = self.get_default_widget_attrs(field)

        formfields[clean_name] = create_field(field, options, default_widget_attrs)

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

    def get_default_widget_attrs(self, field):
        attrs = {}
        try:
            if field["placeholder"]:
                attrs["placeholder"] = field["placeholder"]
        except KeyError:
            pass
        return attrs

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


class EmailNotificationsFormMixin(models.Model):
    email_notifications_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Email notifications enabled"),
        help_text=_("Enable or disable the e-mail notifications"),
    )
    email_notifications_list = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Email notification list"),
        help_text=_(
            "Comma-separated list of e-mail addresses which receive the notifications"
        ),
    )

    email_notification_panels = [
        MultiFieldPanel(
            [
                FieldPanel("email_notifications_enabled"),
                FieldPanel("email_notifications_list"),
            ],
            heading=_("Email notifications"),
        ),
    ]

    class Meta:
        abstract = True

    def get_email_notification_context(self, form_submission):
        form_data = json.loads(form_submission.form_data)
        context = {
            "form": form_submission.form,
            "form_data": form_data,
            "page": form_submission.page,
            "submit_time": form_submission.submit_time,
        }
        return context

    def handle_email_notification(self, email, form_submission, context):
        raise NotImplementedError

    def handle_email_notifications(self, form_submission):
        emails = [x.strip() for x in self.email_notifications_list.split(",")]
        for email in emails:
            logger.info(
                "Email notification (ForSubmission#%s) for '%s'"
                % (form_submission.id, email)
            )
            context = self.get_email_notification_context(form_submission)
            self.handle_email_notification(email, form_submission, context)

    def process_form_submission(self, form, page=None, request=None):
        form_submission = super().process_form_submission(form, page, request=request)
        if self.email_notifications_enabled:
            self.handle_email_notifications(form_submission)
        return form_submission


class WebhooksFormMixin(models.Model):
    webhooks_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Webhooks enabled"),
        help_text=_("Enable to trigger the webhooks when this form is submitted"),
    )
    webhooks = StreamField(
        [
            ("webhook", WebhookBlock()),
        ],
        null=True,
        blank=True,
        verbose_name=_("Webhooks"),
    )

    webhook_panels = [
        MultiFieldPanel(
            [
                FieldPanel("webhooks_enabled"),
                FieldPanel("webhooks"),
            ],
            heading=_("Webhooks"),
        ),
    ]

    class Meta:
        abstract = True

    def handle_webhook(self, webhook, form_submission):
        trigger_webhook(webhook, form_submission)

    def handle_webhooks(self, form_submission):
        for webhook in self.webhooks:
            logger.info("Webhook (ForSubmission#%s)" % form_submission.id)
            self.handle_webhook(dict(webhook.value), form_submission)

    def process_form_submission(self, form, page=None, request=None):
        form_submission = super().process_form_submission(form, page, request=request)
        if self.webhooks_enabled:
            self.handle_webhooks(form_submission)
        return form_submission


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

    def get_uploaded_file_class(self):
        return get_uploaded_file_model()

    def get_form_data(self, form, request=None):
        form_data = form.cleaned_data
        cleaned_form_data = self.clean_form_data(form_data)
        return cleaned_form_data

    def clean_form_data(self, form_data):
        cleaned_form_data = {}
        for key, value in form_data.items():
            if isinstance(value, UploadedFile):
                continue
            cleaned_form_data[key] = value
        return cleaned_form_data

    def process_form_submission(self, form, page=None, request=None):
        form_data = json.dumps(
            self.get_form_data(form, request=request), cls=DjangoJSONEncoder
        )
        form_submission = self.get_submission_class().objects.create(
            form_data=form_data, form=self, page=page
        )
        try:
            for field_name in request.FILES:
                file = request.FILES[field_name]
                uploaded_file = self.get_uploaded_file_class().objects.create(
                    form_submission=form_submission,
                    file=file,
                )
        except AttributeError:
            logger.warning(
                "Could not upload file, WAGTAIL_MODEL_FORMS_UPLOADED_FILE_MODEL is not configured"
            )
        return form_submission
