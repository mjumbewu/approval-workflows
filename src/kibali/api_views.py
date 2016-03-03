from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.statuses import HTTP_202_ACCEPTED
from os.path import join as pathjoin
from kibali.models import Package
from kibali.tasks import (
    create_package as create_package_task
)

from logging import getLogger
logger = getLogger(__name__)

@api_view()
def create_package(request):

    # TODO: At what point should the data be encrypted? Options:
    #   * Encrypt each file in the repository with something like git-crypt
    #   * Encrypt each file BEFORE writing it to the repository
    #   * Encrypt the entire repostory, maybe with git-remote-gcrypt
    #
    # I'm inclined to go with the second option. The commit messages won't be
    # encrypted in that case, but at least unencrypted file data will never be
    # written to disk.
    #
    # I could use a mix of the 2nd and 3rd options, but the decrypted messages
    # will still live on disk for some time when cloned from the encrypted
    # remote.
    #
    # What might be most secure is to encrypt both the files and the commit
    # messages -- or maybe just a portion of the commit message. The downside
    # is that you would never be able to recover the data if you lose the key.
    #
    # However, with git-remote-gcrypt, we may be able to achieve always-
    # encrypted disk storage if we use an in-memory repository for local
    # processing: https://github.com/libgit2/libgit2/issues/18. It seems that
    # if we use libgit2 though, we may not have access to git's native signing
    # features.
    #
    # Another in-memory-like solution is to use a ramdisk. At least then the
    # data gets blown away when the power's cut off. One downside of this is
    # that our storage would be limited by the amount of RAM available in the
    # server. Though that's true of in-memory storage options with libgit2 as
    # well.
    #
    # Regarding the encryption keys, we could store these on AWS maybe, and
    # have the application request them at startup. The AWS keys could be kept
    # in the environment, maybe. This works well when then env vars and the
    # code aren't stored in the same place (Heroku?).
    #
    # Also, the data should probably be encrypted before it even goes into the
    # task queue.

    data = request.data
    package = Package.objects.create()
    task = create_package_task.delay(package.pk, data)
    logger.debug(('Received request to create a new package. Package has '
                  'ID {!r}').format(package.pk))

    # Return a 202 response, since there's still processing going on.
    return Response({
        'package': package.pk,
        'task': task.id,
    }, status_code=HTTP_202_ACCEPTED)


@api_view()
def task_status(request, task_id):
    """
    Report the status of the task identified by the given task_id.

    """

    # Load the celery app, as specified in settings.CELERY_APP
    from importlib import import_module
    modname, appname = settings.CELERY_APP.rsplit('.', 1)
    celery_mod = import_module(modname)
    celery_app = getattr(celery_mod, appname)

    # Look up the task by the given ID
    task = celery_app.AsyncResult(task_id)
    return Response({
        'ready': task.ready(),
        'successful': task.successful(),
        'failed': task.failed(),
        'status': task.status
    })