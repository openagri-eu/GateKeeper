import logging
import re
import requests

from django.http import JsonResponse, HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from urllib.parse import urljoin

from aegis.models import RegisteredService
from aegis.utils.service_utils import match_endpoint, check_service_health

logger = logging.getLogger(__name__)


class GatewayAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def reverse_proxy_handler(self, request, *args, **kwargs):
        import ipdb; ipdb.set_trace()
        # Access the URL argument
        service_name = kwargs.get('service_name', None)
        path = kwargs.get('path', None)

        # Step 1: Match registered service
        try:
            registered_service = RegisteredService.objects.get(status=1, service_name=service_name)  # Only check active services
        except RegisteredService.DoesNotExist:
            return JsonResponse({"error": "Service not registered or active."}, status=404)

        provider_api = registered_service.api_root_url

        url = f"{provider_api}{path}"
        method = request.method
        # Forward all the request headers and body
        headers = {key: value for key, value in request.headers.items() if key != 'Host'}
        params = request.GET.dict()
        data = request.POST.dict()
        json_data = None
        if request.content_type == "application/json" or "application/ld+json":
            try:
                json_data = request.body.decode('utf-8')  # Raw JSON body
            except Exception:
                json_data = None

        # Make the generic request to the target URL
        try:
            response = requests.request(
                method=method,                # HTTP method
                url=url,
                params=params,                # Query parameters
                data=data,                    # Form data
                json=json_data,               # JSON data
                headers=headers,       # Forward headers
                timeout=10                      # probably shoudl set this as an env var
            )
            return HttpResponse(
                response.content,
                status=response.status_code,
                content_type=response.headers.get('Content-Type', 'application/ld+json')
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def dispatch(self, request, *args, **kwargs):
        """
        override django dispatch to always call the same reverse proxy handler,
        independent on the request method
        """
        self.args = args
        self.kwargs = kwargs
        request = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)
            handler = self.reverse_proxy_handler
            response = handler(request, *args, **kwargs)

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response
