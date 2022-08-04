from django.urls import path, reverse
from wagtail.admin.menu import AdminOnlyMenuItem
from wagtail.core import hooks

from wagtail_model_forms.settings import REPORTS
from wagtail_model_forms.views import FormSubmissionReportView

if REPORTS:

    @hooks.register("register_reports_menu_item")
    def register_report_menu_item():
        return AdminOnlyMenuItem(
            FormSubmissionReportView.title,
            reverse("form_submissions_report"),
            classnames="icon icon-" + FormSubmissionReportView.header_icon,
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
