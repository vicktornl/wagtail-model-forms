from django.shortcuts import get_object_or_404
from django.utils.cache import add_never_cache_headers
from django.utils.functional import cached_property

from wagtail_model_forms import get_form_model
from wagtail_model_forms.settings import ADD_NEVER_CACHE_HEADERS


def handle_form_request(request, page):
    if request.method == "POST" and "form_id" in request.POST:
        Form = get_form_model()

        snippet = get_object_or_404(Form, id=int(request.POST.get("form_id")))

        form = snippet.get_form(
            request.POST, request.FILES, page=page, user=request.user
        )

        if form.is_valid():
            request.form_success = snippet.id
            snippet.process_form_submission(form, page=page, request=request)


class FormSnippetMixin:
    block_type = "form"
    streamfields = []

    @cached_property
    def page_has_form(self):
        for field in self.streamfields:
            for block in getattr(self, field):
                if block.block_type == self.block_type:
                    return True
        return False

    def serve(self, request, *args, **kwargs):
        if self.page_has_form:
            if request.method == "POST" and "form_id" in request.POST:
                handle_form_request(request, self)

        res = super().serve(request, *args, **kwargs)

        if ADD_NEVER_CACHE_HEADERS and self.page_has_form:
            add_never_cache_headers(res)

        return res
