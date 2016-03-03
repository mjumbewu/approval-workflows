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

from django.http import HttpResponseNotAllowed
from rest_framework import viewsets


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

def approve_package_view(request, package_id):
    if method not in allowed_methods:
        return HttpResponseNotAllowed(allowed_methods)

    # Look up the location of the package
    package = Package.objects.get(id=package_id)
    # Retrieve the package

    if request.method == 'GET':
        # Load the package signature template
        template = package.get_approval_template()
        # Render the package signature template
        return template(package.get_data())

    elif request.method == 'POST':
        with package:
            # Sign the package as a background task
            package.clone()
            package.sign(actor)
            # Redirect to the signing/signed handler
        pass

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