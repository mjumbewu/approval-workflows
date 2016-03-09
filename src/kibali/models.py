import re
from os.path import join as pathjoin
from uuid import uuid4
from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from logging import getLogger
logger = getLogger(__name__)




#
# Workflow traversal objects
# ==========================

class Package (models.Model):
    """
    A `Package` is an object that moves through a workflow. As the package goes
    from state to state, different actors may be assigned to take actions on the
    package. This may include signing, approving, rejecting, amending, etc.

    You cannot change or remove any packets already in a package. You can only
    add more packets. When an actor takes an action on a package (e.g., signing)
    they are only considered to have taken the action on the content of the
    package up until the point in time of their action.

    * workflow
    * state
    * packets
    * salts (one for each workflow state)
    * signatures
    """
    # workflow = models.ForeignKey('Workflow')
    # current_state = models.ForeignKey('State')
    # content = models.BinaryField()  # The tarred git repository
    repo = models.URLField(null=True, blank=True)

    def _make_repo_url(self):
        return pathjoin(settings.KIBALI_REPO_BASE, str(self.pk) + '.git')

    def init(self, data='{}', commit=True):
        logger.debug(('Initializing new repository for package with '
                      'ID {}').format(package_pk))

        with GitRepo.init() as repo:

            # Create, add, and commit the data file to the repo
            logger.debug('Adding and committing data to the repo at {}'
                         .format(repo.path))
            datafilename = pathjoin(repo.path, 'data.json')
            with open(datafilename, 'w') as datafile:
                datafile.write(data)
            repo.add(datafilename)
            repo.commit(message='Initial Commit')

            # Store the repo
            repo_url = self._make_repo_url()
            logger.debug('Copying the bare repo at {}/.git to {}'
                         .format(repo.path, repo_url))
            copytree(pathjoin(repo.path, '.git'), repo_url)

            # Save the repo location
            self.repo = repo_url
            if commit:
                self.save()

    def sign(self, signing_actor, signing_datetime=None, ):
        if signing_datetime is None:
            signing_datetime = now()


# class Packet (models.Model):
#     """
#     For a git-backed package, each packet will also have its own hash.

#     * data
#     """
#     data


# class Signature (models.Model):
#     """
#     * actor
#     * package
#     """
#     actor
#     package
