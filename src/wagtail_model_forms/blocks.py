from wagtail.core import blocks
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail_model_forms.settings import FORM_MODEL


class AbstractFormBlock(blocks.StructBlock):
    form = SnippetChooserBlock(FORM_MODEL)

    class Meta:
        abstract = True

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        page = context["page"]
        request = context["request"]
        user = request.user
        form_obj = context["self"]["form"]

        if request.method == "POST" and "form_id" in request.POST:
            user = request.user

            form = form_obj.get_form(request.POST, request.FILES, page=page, user=user)
            form.is_valid()
        else:
            form = form_obj.get_form(page=page, user=user)

        context["form"] = form
        return context

    class Meta:
        abstract = True


class FormBlock(AbstractFormBlock):
    class Meta:
        icon = "form"
        template = "wagtail_model_forms/form.html"
