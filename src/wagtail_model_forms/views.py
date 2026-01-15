import json

import django_filters
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
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
    }
    list_export = [
        "form.title",
        "page.title",
        "submit_time",
    ]
    filterset_class = FormSubmissionReportFilterSet

    def _get_form_data_keys_for_submissions(self, submissions):
        """Get unique form_data keys for a specific set of submissions"""
        form_data_keys = []
        seen = set()
        for submission in submissions:
            form_data_json = getattr(submission, "form_data", "{}")
            try:
                form_data_dict = json.loads(form_data_json)
                for key in form_data_dict.keys():
                    if key not in seen:
                        form_data_keys.append(key)
                        seen.add(key)
            except json.JSONDecodeError:
                pass
        return form_data_keys

    def _get_formatted_heading(self, field):
        """Get the formatted heading for a field"""
        heading = self.export_headings.get(field)
        if heading:
            return str(heading)
        return field.replace("-", " ").replace("_", " ").title()
    
    def _get_field_value(self, submission, field):
        """Get a field value from a submission, handling form_data"""
        from wagtail.coreutils import multigetattr
        from django.utils import timezone
        import datetime
        
        if field in ["form.title", "page.title", "submit_time"]:
            value = multigetattr(submission, field)
            # Convert timezone-aware datetime to naive
            if isinstance(value, datetime.datetime) and timezone.is_aware(value):
                value = timezone.make_naive(value, datetime.timezone.utc)
            return value
        else:
            # It's a form_data key
            form_data_json = getattr(submission, "form_data", "{}")
            try:
                form_data_dict = json.loads(form_data_json)
                return form_data_dict.get(field, "")
            except json.JSONDecodeError:
                return ""

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
    
    def write_xlsx(self, queryset, output):
        """Write an xlsx workbook with separate sheets for each form"""
        from openpyxl import Workbook
        from collections import defaultdict
        
        workbook = Workbook(write_only=True, iso_dates=True)
        
        # Group submissions by form
        submissions_by_form = defaultdict(list)
        for submission in queryset:
            form_title = submission.form.title
            submissions_by_form[form_title].append(submission)
        
        # Create a worksheet for each form
        for form_title in sorted(submissions_by_form.keys()):
            submissions = submissions_by_form[form_title]
            
            # Get form_data keys for this specific form
            form_data_keys = self._get_form_data_keys_for_submissions(submissions)
            
            # Build sheet-specific columns
            sheet_columns = ["form.title", "page.title", "submit_time"] + form_data_keys
            
            # Create worksheet with form title (truncate if too long)
            sheet_title = form_title[:31]  # Excel limit is 31 chars
            worksheet = workbook.create_sheet(title=sheet_title)
            
            # Add headers
            headers = [self._get_formatted_heading(field) for field in sheet_columns]
            worksheet.append(headers)
            
            # Add rows
            for submission in submissions:
                row_values = [self._get_field_value(submission, field) for field in sheet_columns]
                worksheet.append(row_values)
        
        workbook.save(output)
    


class FormSubmissionDetailView(InspectView):
    model = FormSubmission
    index_url_name = "form_submissions_report"
    delete_url_name = "delete_form_submission"
    edit_url_name = "edit_form_submission"
    header_icon = "form"
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
    header_icon = "form"
    fields = ["status"]


class DeleteFormSubmissionView(DeleteView):
    model = FormSubmission
    index_url_name = "form_submissions_report"
    delete_url_name = "delete_form_submission"
    edit_url_name = "edit_form_submission"
    header_icon = "form"
