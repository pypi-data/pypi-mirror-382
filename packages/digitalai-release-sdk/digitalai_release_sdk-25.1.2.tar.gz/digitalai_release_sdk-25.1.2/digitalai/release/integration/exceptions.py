class AbortException(BaseException):
    """Exception class to be raised when a process needs to be prematurely terminated.

    This exception can be caught and handled by the calling code to gracefully terminate
    the process and clean up any resources before exiting.
    """
    pass

