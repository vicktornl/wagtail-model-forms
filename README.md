# Wagtail Model Forms

[![Version](https://img.shields.io/pypi/v/wagtail-model-forms.svg?style=flat)](https://pypi.python.org/pypi/wagtail-model-forms/)
![CI](https://github.com/vicktornl/wagtail-model-forms/actions/workflows/ci.yml/badge.svg)

The Wagtail Form Builder functionalities available for your models/snippets.

## Requirements

- Python 3
- Django >= 2.2.8
- Wagtail >= 2

## Installation

Install the package

```
pip install wagtail-model-forms
```

Add `wagtail_model_forms` to your INSTALLED_APPS

```
INSTALLED_APPS = [
    ...
    "wagtail_model_forms",
]
```

Create your models

```
from modelcluster.fields import ParentalKey
from wagtail_model_forms.models import AbstractForm, AbstractFormField, AbstractFormSubmission


class FormField(AbstractFormField):
    model = ParentalKey(
        "Form",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class FormSubmission(AbstractFormSubmission):
  pass


class Form(AbstractForm):
  pass
```

## Settings

`WAGTAIL_MODEL_FORMS_ADD_NEVER_CACHE_HEADERS`

Default `True`

`WAGTAIL_MODEL_FORMS_FORM_MODEL`

Default `wagtail_model_forms.models.Form`

`WAGTAIL_MODEL_FORMS_SUBMISSION_MODEL`

Default `wagtail_model_forms.models.FormSubmission`
