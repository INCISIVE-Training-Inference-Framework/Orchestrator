from __future__ import unicode_literals

import logging
import traceback

from rest_framework import status
from rest_framework.views import Response, exception_handler

from main.exceptions import InternalError, UserError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, InternalError) and not response:
        traceback.print_exception(type(exc.get_exception()), exc.get_exception(), exc.get_exception().__traceback__)
        response = Response(
            {
                f'{exc.get_message()}'
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
    elif response is None:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        response = Response(
            {
                f'Unexpected internal error'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    logger.error(response.data)
    return response
