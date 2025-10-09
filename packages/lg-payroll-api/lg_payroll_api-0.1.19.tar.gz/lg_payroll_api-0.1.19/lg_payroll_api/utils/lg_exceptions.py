class LgException(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class LgParameterListLimitException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"ERROR - {message}")


class LgInconsistencyException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG INCONSISTENCY - {message}")


class LgErrorException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG ERROR - {message}")


class LgNotProcessException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG NOT PROCESS - {message}")


class LgTaskExecutionException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG TASK EXECUTION ERROR - {message}")


class LgTaskCancelledException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG TASK CANCELLED - {message}")


class LgTaskNotRespondingException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG TASK NOT RESPONDING - {message}")


class LgTaskCompletedWithInconsistenciesException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG TASK COMPLETED WITH INCONSISTENCIES - {message}")


class LgTaskNotCompletedYetException(LgException):
    def __init__(self, message: str) -> None:
        super().__init__(f"LG TASK NOT COMPLETED YET - {message}")
