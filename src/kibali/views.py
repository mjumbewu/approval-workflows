"""
Approvio UI Views
-----------------

**Workflow layout**
- Circles and lines -- building a state machine

**User's queue**
- List of things that are assigned to a particular user

**Approval/signature**
- A [templated] view of the data received so far, and a "signature" box



Administration API Views
------------------------

**C/R/U/D workflows**



Usage API Views & Web Hooks
---------------------------

**Create a package**

**Update data/files in a package**

**Sign a package**

"""

import json
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
)
from django.template import RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_safe
from django.shortcuts import get_object_or_404, render
from kibali.models import Package, SignatureConfiguration, Actor
from kibali.tasks import (
    create_package as create_package_task
)
from rest_framework import viewsets

from logging import getLogger
logger = getLogger(__name__)


# Workflow Layouts and Approval/Signature UI
# ==========================================

def workflow_builder_view(request):
    pass

def assignment_list_view(request):
    """
    Show a list of the packages that are waiting on the current user, filterable
    by workflow.
    """
    pass

@csrf_exempt
@require_http_methods(['POST'])
def create_package_view(request, config_key):
    # Get the signature configuration record for this request.
    config = get_object_or_404(SignatureConfiguration, application_key=config_key)

    host = request.get_host()
    if not config.is_host_allowed(host):
        context = {'reason': 'Host {} is not allowed.'.format(host)}
        return render('403.html', context=context, status=403)

    # Load the data from the request.
    if request.META['CONTENT_TYPE'] == 'application/json':
        data = json.loads(request.read())
    else:
        data = request.POST

    # Create a new package.
    package = Package.objects.create()
    # package = Package.objects.create_for_signature(config)
    logger.debug('Received request to create a new package. Package has ID {!r}'.format(package.pk))

    # Encode/encrypt the data for storage in the new package.
    encoded_data = json.dumps(data, sort_keys=True, indent=1)
    task = create_package_task.delay(package.pk, encoded_data)
    package.send_signature_invitation()

    sign_url = 'http://' + request.get_host() + reverse('ui-sign-package', args=(config.application_key, package.pk))
    send_mail('Sign a package', 'Sign the package at ' + sign_url,
              'mjumbewu@gmail.com', [data['email']])

    # For ajax, return a 202 response, since there's still processing
    # going on in the background.
    if request.is_ajax():
        return JsonResponse({
            'package': package.pk,
            'task': task.id,
        }, status=HTTP_202_ACCEPTED)

    # Otherwise, redirect according to the config.
    # TODO: Have a default success page if no redirect_url is supplied.
    else:
        return HttpResponseRedirect(redirect_to=config.created_redirect_url)

@require_http_methods(['GET', 'POST'])
def sign_package_view(request, config_key, package_pk):
    # Look up the location of the package
    config = get_object_or_404(SignatureConfiguration, application_key=config_key)
    package = get_object_or_404(Package, pk=package_pk)

    if request.method == 'GET':
        # Render the package signature template with the package data
        template = get_template('kibali/sign_package.html').render
        data = package.get_data()
        context = RequestContext(request, {'data': data})
        return HttpResponse(template(context))

    elif request.method == 'POST':
        redirect_url = config.signed_redirect_url or ''
        actor = Actor.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
        )
        # Sign the package as a background task, and redirect to the
        # signing/signed handler
        package.sign(actor)
        return HttpResponseRedirect(redirect_to=redirect_url)

# @require_safe
# def


# Workflow Building/Administration API
# ====================================

class WorkflowViewSet (viewsets.ViewSet):
    """
    Create, retieve, update, and delete workflows.
    """
    lookup_field = 'slug'

    def list(self, request):
        pass


# Approval/signature API
# ======================

def start_workflow_view(request, workflow_slug):
    """
    Create a new package and start it through the workflow identified by the
    given slug.

    POST /api/1/:workflow_slug/packages/

        Body: <some JSON data>

    """
    # Create a new package model instance and return the URL with a status of
    # 202.
    #
    # LOG that the user started a workflow with some data.
    #
    # Kick off a background process to initialize the repository. If there
    # is POST data in the request, use that as the initial data.
    #
    # Evaluate the conditions from the start state using the initial data to
    # transition the package to the appropriate state. Fire off the appropriate
    # follow-transition and enter-state events.
    #
    # LOG that a package was transitioned from one state to another.