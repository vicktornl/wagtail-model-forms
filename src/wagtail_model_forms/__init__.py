from django.core.exceptions import ImproperlyConfigured

from wagtail_model_forms import settings


def get_form_model():
    from django.apps import apps

    model_string = settings.FORM_MODEL
    try:
        return apps.get_model(model_string, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAIL_MODEL_FORMS_FORM_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAIL_MODEL_FORMS_FORM_MODEL refers to model '%s' that has not been installed"
            % model_string
        )


def get_submission_model():
    from django.apps import apps

    model_string = settings.SUBMISSION_MODEL
    try:
        return apps.get_model(model_string, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAIL_MODEL_FORMS_SUBMISSION_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAIL_MODEL_FORMS_SUBMISSION_MODEL refers to model '%s' that has not been installed"
            % model_string
        )
