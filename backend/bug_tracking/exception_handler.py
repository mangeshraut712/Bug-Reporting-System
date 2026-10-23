"""
Custom exception handler for DRF.
"""
import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

GENERIC_RESPONSES = {
    status.HTTP_401_UNAUTHORIZED: (
        'Unauthorized',
        'Authentication credentials were not provided or are invalid.',
    ),
    status.HTTP_403_FORBIDDEN: (
        'Forbidden',
        'You do not have permission to perform this action.',
    ),
    status.HTTP_404_NOT_FOUND: (
        'Not Found',
        'The requested resource was not found.',
    ),
    status.HTTP_429_TOO_MANY_REQUESTS: (
        'Too Many Requests',
        'Too many requests. Try again later.',
    ),
}


def custom_exception_handler(exc, context):
    """
    Format API errors consistently and keep unexpected failures out of the response body.
    """
    response = exception_handler(exc, context)

    if response is None or response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.exception('Unhandled API error')
        return Response(
            {'error': 'Server Error', 'message': 'An unexpected error occurred.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    mapped = GENERIC_RESPONSES.get(response.status_code)
    if mapped is not None:
        error, message = mapped
        response.data = {'error': error, 'message': message}
    return response
