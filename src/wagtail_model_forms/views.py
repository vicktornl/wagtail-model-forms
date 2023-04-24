import django_filters
from django.utils.translation import gettext_lazy as _
from wagtail.admin.filters import DateRangePickerWidget, WagtailFilterSet
from wagtail.admin.views.reports import ReportView

from wagtail_model_forms import get_submission_model

FormSubmission = get_submission_model()


class FormSubmissionReportFilterSet(WagtailFilterSet):
    submit_time = django_filters.DateFromToRangeFilter(
        label=_("Date / Time"), widget=DateRangePickerWidget
    )

    class Meta:
        model = FormSubmission
        fields = ["submit_time", "form"]


class FormSubmissionReportView(ReportView):
    template_name = "wagtail_model_forms/form_submissions_report.html"
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

    def get_filename(self):
        return "form-submissions"

    def get_queryset(self):
        return (
            FormSubmission.objects.all()
            .select_related("form")
            .select_related("page")
            .order_by("-submit_time")
        )
