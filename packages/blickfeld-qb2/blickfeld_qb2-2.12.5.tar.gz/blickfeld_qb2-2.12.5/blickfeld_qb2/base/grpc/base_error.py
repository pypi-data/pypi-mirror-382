from grpc import StatusCode
from grpc.aio import AioRpcError


class BaseError(Exception):
    def __init__(self, code: StatusCode, message: str | None = None) -> None:
        super().__init__(code, message)
        #: :py:class:`~grpc.StatusCode` of the error
        self.code = code
        #: Error message
        self.message = message

    @staticmethod
    def create_from_exception(ex: Exception) -> "BaseError":
        if isinstance(ex, BaseError):
            return ex
        if isinstance(ex, AioRpcError):
            raise BaseError(
                ex.code(),
                ex.details(),
            )

        return BaseError(StatusCode.UNKNOWN, str(ex))
