import json

import django_filters
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView
from wagtail import VERSION as WAGTAIL_VERSION
from wagtail.admin.filters import DateRangePickerWidget, WagtailFilterSet
from wagtail.admin.views.generic import DeleteView, EditView, InspectView
from wagtail.admin.views.reports import ReportView

from wagtail_model_forms import get_submission_model

FormSubmission = get_submission_model()


class FormSubmissionReportFilterSet(WagtailFilterSet):
    submit_time = django_filters.DateFromToRangeFilter(
        label=_("Date / Time"), widget=DateRangePickerWidget
    )

    class Meta:
        model = FormSubmission
        fields = ["submit_time", "form", "status"]


class FormSubmissionReportView(ReportView):
    index_url_name = "form_submissions_report"
    index_results_url_name = "form_submissions_report_results"
    results_template_name = "wagtail_model_forms/form_submissions_report_results.html"
    title = _("Form submissions")
    header_icon = "form"
    export_headings = {
        "form.title": _("Form"),
        "page.title": _("Page"),
        "submit_time": _("Date / Time"),
        "form_data": _("Data"),
    }
    list_export = [
        "form.title",
        "page.title",
        "submit_time",
        "form_data",
    ]
    filterset_class = FormSubmissionReportFilterSet

    # COMPAT: remove fallback template when Wagtail 6.2 is the minimum version
    def get_template_names(self):
        if WAGTAIL_VERSION < (6, 2):
            return ["wagtail_model_forms/compat/form_submissions_report.html"]
        return super().get_template_names()

    @property
    # COMPAT: move to direct attribute assignment when Wagtail 6.2 is the minimum version
    def page_title(self):
        return self.title

    def get_filename(self):
        return "form-submissions"

    def get_queryset(self):
        return (
            FormSubmission.objects.all()
            .select_related("form")
            .select_related("page")
            .order_by("-submit_time")
        )


class FormSubmissionDetailView(InspectView):
    model = FormSubmission
    index_url_name = "form_submissions_report"
    delete_url_name = "delete_form_submission"
    edit_url_name = "edit_form_submission"
    _show_breadcrumbs = True

    def get_page_title(self):
        return str(self.object.form)

    def get_breadcrumbs_items(self):
        return self.breadcrumbs_items + [
            {
                "url": reverse_lazy("form_submissions_report"),
                "label": _("Form submissions"),
            },
            {"url": "", "label": str(self.object.form)},
        ]

    def get_fields(self):
        fields = [
            "form",
            "page",
            "submit_time",
            "status",
            "form_data",
            "uploaded_files",
        ]
        return fields

    def get_field_label(self, field_name, field):
        if field_name == "form_data":
            return _("Submitted form data")
        if field_name == "uploaded_files":
            return _("Uploaded files")
        return super().get_field_label(field_name, field)

    def get_field_display_value(self, field_name, field):
        if field_name == "form_data":
            result = ""
            form_data = getattr(self.object, field_name)
            form_data = json.loads(form_data)
            for key, value in form_data.items():
                if value:
                    result += "%s: %s<br>" % (key, value)
            return format_html(result)

        if field_name == "uploaded_files":
            result = "<ul>"
            for uploaded_file in getattr(
                self.object, field_name, FormSubmission.objects.none()
            ).all():
                result += '<li><a href="%s" target="_blank">%s</a></li>' % (
                    uploaded_file.download_url,
                    uploaded_file.file.name,
                )
            result += "</ul>"
            return format_html(result)

        return super().get_field_display_value(field_name, field)


class EditFormSubmissionView(EditView):
    model = FormSubmission
    index_url_name = "form_submissions_report"
    delete_url_name = "delete_form_submission"
    edit_url_name = "edit_form_submission"
    fields = ["status"]


class DeleteFormSubmissionView(DeleteView):
    model = FormSubmission
    index_url_name = "form_submissions_report"
    delete_url_name = "delete_form_submission"
    edit_url_name = "edit_form_submission"
