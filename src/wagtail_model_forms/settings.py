from django.conf import settings


def get_setting(name: str, default=None):
    return getattr(settings, "WAGTAIL_MODEL_FORMS_%s" % name, default)


ADD_NEVER_CACHE_HEADERS = get_setting("ADD_NEVER_CACHE_HEADERS", default=True)
FORM_MODEL = get_setting("FORM_MODEL", default="")
SUBMISSION_MODEL = get_setting("SUBMISSION_MODEL", default="")
REPORTS = get_setting("REPORTS", default=True)

CIRSPY_FORMS_FORM_TAG = get_setting("CIRSPY_FORMS_FORM_TAG", default=False)
