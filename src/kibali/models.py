import json
import re
from os.path import join as pathjoin
from shutil import copytree
from uuid import uuid4
from django.conf import settings
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from gitutils import GitRepo

from logging import getLogger
logger = getLogger(__name__)


#
# Form/signature configuration
# ============================

class SignatureConfiguration (models.Model):
    label = models.TextField(help_text=_("The human-readable name for the application using the signatures. Primarily used for record-keeping and organization."))
    application_key = models.CharField(max_length=36, unique=True, default=uuid4, db_index=True)
    allowed_domains = models.TextField(default='*', help_text=_(
        "List the domains that are allowed to submit data for "
        "approval. Each domain should go on its own line. You can use "
        "wildcards ? and *. For example:<br>"
        "&nbsp;&nbsp;&nbsp; &bull; &nbsp; <code>phila.gov</code><br>"
        "&nbsp;&nbsp;&nbsp; &bull; &nbsp; <code>*.phila.gov</code><br>"
        "&nbsp;&nbsp;&nbsp; &bull; &nbsp; <code>phila.???</code>"))
    workflow = models.ForeignKey('workflows.Workflow')
    # created_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected after data is submitted to the system, if by form POST. If this is left blank, a default page will be used."))
    # created_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded after being received."))
    # signed_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected after signing data. If this is left blank, a default page will be used."))
    # signed_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded after being signed."))

    def is_host_allowed(self, hostname):
        for hostpattern in self.allowed_domains.split():
            hostpattern = hostpattern.replace('.', r'\.')
            hostpattern = hostpattern.replace('*', r'.*')
            hostpattern = hostpattern.replace('?', r'.?')
            if re.match('^' + hostpattern + '$', hostname):
                return hostpattern
        return False

    def __str__(self):
        return self.label


#
# Workflow traversal objects
# ==========================

class PackageManager (models.Manager):
    def create_for_signature(self, config):
        return self.create(config=config)


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
    workflow = models.ForeignKey('workflkow.Workflow')
    current_state = models.ForeignKey('workflow.State')
    # content = models.BinaryField()  # The tarred git repository
    repo = models.URLField(null=True, blank=True)
    # config = models.ForeignKey('SignatureConfiguration', null=True, blank=True)

    objects = PackageManager()

    def __str__(self):
        return self.repo or ''

    def _make_repo_url(self):
        return pathjoin(settings.KIBALI_REPO_BASE, str(self.pk) + '.git')

    def init(self, data='{}', commit=True):
        logger.debug(('Initializing new repository for package with '
                      'ID {}').format(self.pk))

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

    def get_data(self):
        logger.debug('Cloning repository for package with ID {}'.format(self.pk))
        with GitRepo.clone(self.repo) as repo:
            datafilename = pathjoin(repo.path, 'data.json')
            with open(datafilename) as datafile:
                data = json.load(datafile)
        return data

    def sign(self, signing_actor, signing_datetime=None, ):
        if signing_datetime is None:
            signing_datetime = now()

        with GitRepo.clone(self.repo) as repo:
            tagname = '{}.{}'.format(hash(signing_actor),
                                     hash(signing_datetime))
            repo.tag(tagname,
                     "{} took action {} at {}".format(signing_actor, 'sign',
                                                      signing_datetime))
            repo.push(tags=True)


class SignatureInvitation (models.Model):
    package = models.ForeignKey('Package')
    actor = models.ForeignKey('Actor')
    short_code = models.TextField()


class Actor (models.Model):
    """
    An Actor represents the person who is doing the signing, approving,
    rejecting, amending, etc.
    """
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return self.name


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
