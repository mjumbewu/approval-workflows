from celery import shared_task
from kibali.models import Package

from logging import getLogger
logger = getLogger(__name__)


@shared_task
def create_package(package_pk, data):
    package = Package.objects.get(pk=package_pk)
    package.init(data=data)
