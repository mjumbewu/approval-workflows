from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now


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
    repo = models.URLField()

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
