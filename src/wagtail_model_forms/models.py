import json

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import (
    AbstractFormField as WagtailAbstractFormField,
)
from wagtail.contrib.forms.models import (
    AbstractFormSubmission as WagtailAbstractFormSubmission,
)

from wagtail_model_forms import get_submission_model
from wagtail_model_forms.settings import FORM_MODEL


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


class AbstractForm(ClusterableModel):
    title = models.CharField(
        verbose_name=_("title"),
        max_length=255,
    )

    form_builder = FormBuilder

    form_panels = [
        FieldPanel("title", classname="full"),
        InlinePanel("form_fields", label="Form fields"),
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
        return self.form_fields.all()

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
