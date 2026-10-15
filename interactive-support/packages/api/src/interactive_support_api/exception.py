from fastapi import status


class ApiError(Exception):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class ConversationNotFound(ApiError):
    status_code = status.HTTP_404_NOT_FOUND


class ActionNotFound(ApiError):
    status_code = status.HTTP_409_CONFLICT
