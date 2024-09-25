import json

import requests
from django.template import Context, Template


def trigger_webhook(webhook, form_submission):
    form_data = json.loads(form_submission.form_data)

    context = Context(form_data)

    url = Template(webhook["url"]).render(context)
    method = webhook["method"]
    request_headers = webhook["request_headers"]
    request_body = webhook["request_body"]

    headers = None
    data = None

    if request_headers:
        headers = {}
        for request_header in request_headers:
            headers[request_header["field_name"]] = Template(
                request_header["field_value"]
            ).render(context)

    if request_body and request_body != "":
        data = json.loads(Template(request_body).render(context))
    else:
        data = None

    res = requests.request(method.upper(), url=url, headers=headers, data=data)
    return res
