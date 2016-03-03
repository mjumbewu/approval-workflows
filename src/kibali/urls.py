from django.conf.urls import url
from kibali.api_views import (
    create_package as create_package_view
)

urlpatterns = [
    url(r'^package/', create_package_view, name='api-create-package'),
]
