"""
Custom exception handler for DRF.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats error responses consistently.
    """
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == 401:
            response.data = {
                'error': 'Unauthorized',
                'message': 'Authentication credentials were not provided or are invalid.'
            }
        elif response.status_code == 403:
            response.data = {
                'error': 'Forbidden',
                'message': 'You do not have permission to perform this action.'
            }
        elif response.status_code == 404:
            response.data = {
                'error': 'Not Found',
                'message': 'The requested resource was not found.'
            }

    return response
