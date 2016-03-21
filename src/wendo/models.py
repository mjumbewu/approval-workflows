from django.db import models
from django.contrib.postgres.fields import ArrayField


#
# Workflow templates
# ==================

class Workflow (models.Model):
    """
    A workflow template object. There are four models that work together to
    make up a workflow template: A `Workflow` is made of a number of `State`
    nodes. These states are connected to each other by `Transition` rules. At
    each state, a particular `Actor` is responsible for moving the workflow
    forward.

    The `Workflow`, `State` and `Transition` objects make up a kind of finite
    state machine.

    Attributes:
    -----------
    * actors
    * states

    Methods:
    --------
    * start

      Create a new package with the given data/files. Move that package into
      the initial state.

    Events:
    -------
    * start
    * finish
    """
    name = models.TextField()
    slug = models.SlugField()
    on_start_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded when the state is entered."))
    on_finish_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded when the state is left."))
    on_start_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected when the state is entered, if by form POST and neither the previous state or transition had a redirect URL. If this is left blank, a default page will be used."))
    on_finish_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected when the state is left, if by form POST. If this is left blank, the system will try to use the redirect URL from the transition or the enter condition of the next state. Otherwise, a default page will be used."))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = (self.id is None)
        super().save(*args, **kwargs)

        if is_new:
            self.start_state = State.objects.create(
                name='Start',
                workflow=self)
            self.end_state = State.objects.create(
                name='End',
                workflow=self)
            Transition.objects.create(
                from_state=self.start_state,
                to_state=self.end_state)

    def to_dict(self):
        data = {
            'actors': [],
            'states': [],
        }

        for actor in self.actors.all():
            data['actors'].append({'name': actor.name})
        for state in self.states.all():
            data['states'].append(state.to_json())

        data['start'] = self.start_state.name
        data['end'] = self.end_state.name

        return data


class State (models.Model):
    """
    Part of the workflow template structure. See `Workflow` for more.

    Attributes:
    ----------
    * name
    * assignment
    * actions
    * transitions

      Outbound transitions from this state. Inbound transitions are available
      via the ``reverse_transitions`` attribute.

    Events:
    ------
    * enter
    * leave
    """
    name = models.TextField()
    assignment = models.ForeignKey('Actor', null=True)
    actions = ArrayField(models.TextField(), null=True)
    workflow = models.ForeignKey('Workflow', related_name='states', on_delete=models.CASCADE)
    on_enter_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded when the state is entered."))
    on_leave_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded when the state is left."))
    on_enter_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected when the state is entered, if by form POST and neither the previous state or transition had a redirect URL. If this is left blank, a default page will be used."))
    on_leave_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected when the state is left, if by form POST. If this is left blank, the system will try to use the redirect URL from the transition or the enter condition of the next state. Otherwise, a default page will be used."))

    def __str__(self):
        return '{} in {}'.format(self.name, self.workflow.name)

    def to_dict(self):
        data = {
            'name': self.name,
            'assign': self.assignment.name if self.assignment else None,
            'actions': self.actions or [],
            'then': [],
        }

        for transition in self.transitions.all():
            data['then'].append(transition.to_json())

        return data


class Transition (models.Model):
    """
    Part of the workflow template structure. See `Workflow` for more.

    Attributes:
    ----------
    * from_state
    * to_state
    * condition

    Events:
    ------
    * follow
    """
    condition = models.TextField(default='True')
    from_state = models.ForeignKey('State', related_name='transitions', on_delete=models.CASCADE)
    to_state = models.ForeignKey('State', related_name='reverse_transitions')
    on_follow_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded when the state is entered."))
    on_leave_callback_url = models.URLField(null=True, blank=True, help_text=_("The URL to which the package data will be forwarded when the state is left."))
    on_follow_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected when the state is entered, if by form POST and neither the previous state or transition had a redirect URL. If this is left blank, a default page will be used."))
    on_leave_redirect_url = models.URLField(null=True, blank=True, help_text=_("The page to which the user will be redirected when the state is left, if by form POST. If this is left blank, the system will try to use the redirect URL from the transition or the enter condition of the next state. Otherwise, a default page will be used."))

    class Meta:
        order_with_respect_to = 'from_state'

    def __str__(self):
        return 'From {} to {}'.format(self.from_state, self.to_state)

    def to_dict(self):
        data = {
            'goto': self.to_state.name,
            'when': self.condition,
        }

        return data


class Role (models.Model):
    """
    Part of the workflow template structure. See `Workflow` for more.

    A role describes the actor or set of actors that may take an action at a
    particular state in a workflow.

    Attributes:
    ----------
    * name
    """
    workflow = models.ForeignKey('Workflow', related_name='actors')
    name = models.TextField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True)
    emails = models.TextField(default='', blank=True)

    def __str__(self):
        return '{} in {}'.format(self.name, self.workflow.name)
