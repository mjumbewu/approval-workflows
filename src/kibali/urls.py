from django.conf.urls import url
from kibali.views import create_package_view, sign_package_view
from kibali.api_views import (
    task_status as task_status_view,
)

urlpatterns = [
    url(r'^(.+)/package/(.+)/sign$', sign_package_view, name='ui-sign-package'),
    url(r'^(.+)/package/$', create_package_view, name='ui-create-package'),
    url(r'^task-status/(.+)$', task_status_view, name='api-task-status'),
]
