from celery import shared_task
from gitutils import GitRepo
from kibali.models import Package

from logging import getLogger
logger = getLogger(__name__)


@shared_task
def create_package(package_pk, data):
    logger.debug('Initializing new repository for package with ID {}'.format(
        package_pk))

    pacakge = Package.objects.get(pk=package_pk)

    with GitRepo.init() as repo:

        # Create, add, and commit the data file to the repo
        datafilename = pathjoin(repo, 'data.json')
        with open(datafilename, 'w') as datafile:
            json.dump(data, datafile, sort_keys=True, indent=1)
        repo.add(datafilename)
        repo.commit(message='Initial Commit')

        # Store the repo
        repo.add_remote('origin', '')
        repo.push()
