# middleware
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse

from app_auth.models import *


class IsUserAdmin:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow superusers to bypass all checks
        if request.user.is_superuser:
            return self.get_response(request)

        # Redirect unauthenticated users to the login page
        if not request.user.is_authenticated:
            if request.path != reverse('login'):
                return redirect('login')
            return self.get_response(request)

        # Check if the user has UserDetails and a valid role
        try:
            user_details = request.user.details  # Access UserDetails using related_name='details'
        except AttributeError:
            return HttpResponseForbidden("Oops: We did not find any role for this user.")

        # Define allowed roles
        allowed_roles = ['admin', ]

        # Check if the user's role is allowed
        if user_details.user_role not in allowed_roles:
            return HttpResponseForbidden("Forbidden: You do not have permission to access this page.")

        # Allow access to the requested page
        return self.get_response(request)
        
        