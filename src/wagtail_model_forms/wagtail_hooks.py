from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.site_summary import SummaryItem

from wagtail_model_forms import get_submission_model
from wagtail_model_forms.settings import REPORTS
from wagtail_model_forms.views import (
    DeleteFormSubmissionView,
    EditFormSubmissionView,
    FormSubmissionDetailView,
    FormSubmissionReportView,
)

FormSubmission = get_submission_model()


class ReportMenuItem(MenuItem):
    def is_shown(self, request):
        return REPORTS


class ReportSummaryItem(SummaryItem):
    order = 500
    template_name = "wagtail_model_forms/summary.html"

    def get_context_data(self, parent_context):
        return {
            "new_form_submissions": FormSubmission.objects.filter(
                status=FormSubmission.Status.NEW
            ).count(),
        }

    def is_shown(self):
        return REPORTS


if REPORTS:

    @hooks.register("construct_homepage_summary_items")
    def add_report_item(request, items):
        items.append(ReportSummaryItem(request))

    @hooks.register("register_reports_menu_item")
    def register_report_menu_item():
        return ReportMenuItem(
            FormSubmissionReportView.title,
            reverse("form_submissions_report"),
            icon_name=FormSubmissionReportView.header_icon,
            order=700,
        )

    @hooks.register("register_admin_urls")
    def register_report_url():
        return [
            path(
                "reports/form-submissions/",
                FormSubmissionReportView.as_view(),
                name="form_submissions_report",
            ),
            path(
                "reports/form-submissions/<int:pk>/",
                FormSubmissionDetailView.as_view(),
                name="form_submissions_detail",
            ),
            path(
                "reports/form-submissions/<int:pk>/edit/",
                EditFormSubmissionView.as_view(),
                name="edit_form_submission",
            ),
            path(
                "reports/form-submissions/<int:pk>/delete/",
                DeleteFormSubmissionView.as_view(),
                name="delete_form_submission",
            ),
            path(
                "reports/form-submissions/results/",
                FormSubmissionReportView.as_view(results_only=True),
                name="form_submissions_report_results",
            ),
        ]
