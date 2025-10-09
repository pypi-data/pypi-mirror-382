from django.conf import settings

from .dashboard_templates import dashboard_templates


class DashboardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, *args):  # noqa: ARG002
        """Adds/Updates references to templates."""
        try:
            template_data = settings.SUBJECT_DASHBOARD_BASE_TEMPLATES
        except AttributeError:
            template_data = dashboard_templates
        request.template_data.update(**template_data)

    def process_template_response(self, request, response):
        if response.context_data:
            response.context_data.update(**request.url_name_data)
            response.context_data.update(**request.template_data)
        return response
