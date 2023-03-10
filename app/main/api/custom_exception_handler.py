from __future__ import unicode_literals

import logging

from rest_framework import status
from rest_framework.views import Response, exception_handler

from main.exceptions import InternalError, UserError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, InternalError) and not response:
        logger.error(exc.internal_message)
        response = Response(
            {
                f'{exc.public_message}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    elif isinstance(exc, UserError) and not response:
        response = Response(
            {
                f'{exc.message}'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if response is None:
        logger.error(exc)
        response = Response(
            {
                f'Unexpected internal error'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    logger.error(response.data)
    return response
