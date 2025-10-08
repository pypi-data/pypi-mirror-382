# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

"""Exceptions raised by the assets API client."""

from frequenz.client.base.exception import (
    ApiClientError,
    ClientNotConnected,
    DataLoss,
    EntityAlreadyExists,
    EntityNotFound,
    GrpcError,
    InternalError,
    InvalidArgument,
    OperationAborted,
    OperationCancelled,
    OperationNotImplemented,
    OperationOutOfRange,
    OperationPreconditionFailed,
    OperationTimedOut,
    OperationUnauthenticated,
    PermissionDenied,
    ResourceExhausted,
    ServiceUnavailable,
    UnknownError,
    UnrecognizedGrpcStatus,
)

__all__ = [
    "ApiClientError",
    "ClientNotConnected",
    "DataLoss",
    "EntityAlreadyExists",
    "EntityNotFound",
    "GrpcError",
    "InternalError",
    "InvalidArgument",
    "OperationAborted",
    "OperationCancelled",
    "OperationNotImplemented",
    "OperationOutOfRange",
    "OperationPreconditionFailed",
    "OperationTimedOut",
    "OperationUnauthenticated",
    "PermissionDenied",
    "ResourceExhausted",
    "ServiceUnavailable",
    "UnknownError",
    "UnrecognizedGrpcStatus",
    "PermissionDenied",
]
