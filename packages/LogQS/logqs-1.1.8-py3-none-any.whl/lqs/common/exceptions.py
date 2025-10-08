import sys
import json
import traceback


class BadRequestException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed due to a conflict."
        )
        super().__init__(self.message)


class UnauthorizedException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed since the user is not authenticated."
        )
        super().__init__(self.message)


class ForbiddenException(Exception):
    def __init__(self, action=None, resource=None, reason=None, msg=None):
        if msg is not None:
            self.message = msg
        else:
            self.message = (
                f"Action '{action}' on '{resource}' not allowed for the current user."
            )
            if reason is not None:
                self.message = f"Action '{action}' on '{resource}' not allowed for the current user: {reason}"
        super().__init__(self.message)


class NotFoundException(Exception):
    def __init__(self, resource=None, resource_id=None, msg=None):
        if msg is not None:
            self.message = msg
        else:
            if resource is not None:
                if resource_id is not None:
                    self.message = f"{resource} with ID {resource_id} not found."
                else:
                    self.message = f"{resource} not found."
            else:
                self.message = "Resource not found."
        super().__init__(self.message)


class InternalServerErrorException(Exception):
    def __init__(self, msg=None):
        if msg is not None:
            self.message = msg
        else:
            (
                exception_type,
                exception_value,
                exception_traceback,
            ) = sys.exc_info()
            traceback_string = traceback.format_exception(
                exception_type, exception_value, exception_traceback
            )
            err_msg = {
                "errorType": exception_type.__name__
                if exception_type
                else "UnknownError",
                "errorMessage": str(exception_value),
                "stackTrace": traceback_string,
            }
            self.message = json.dumps(err_msg)
        super().__init__(self.message)


class ConflictException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed due to a conflict."
        )
        super().__init__(self.message)


class ContentTooLargeException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed due to the content being too large."
        )
        super().__init__(self.message)


class LockedException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed due to a lock."
        )
        super().__init__(self.message)


class NotImplementedException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed since the requested service is not implemented."
        )
        super().__init__(self.message)


class TimeoutException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed due to a timeout."
        )
        super().__init__(self.message)


class DataStoreNotFoundException(Exception):
    def __init__(self, datastore_name=None):
        self.message = "DataStore not found."
        if datastore_name is not None:
            self.message = f"DataStore {datastore_name} not found."


class LogIntegrityException(Exception):
    def __init__(self, msg=None):
        self.message = (
            msg
            if msg is not None
            else "The request couldn't be processed due to a log integrity error."
        )
        super().__init__(self.message)


# Process Exceptions


class AsyncIngestionError(Exception):
    pass
