from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from wagtail_model_forms.settings import REPORTS
from wagtail_model_forms.views import FormSubmissionReportView


class ReportsMenuItem(MenuItem):
    def is_shown(self, request):
        return REPORTS


if REPORTS:

    @hooks.register("register_reports_menu_item")
    def register_report_menu_item():
        return ReportsMenuItem(
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
        ]
