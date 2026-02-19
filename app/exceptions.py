"""Domain exception hierarchy."""


class AppError(Exception):
    """Base class for all application domain errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource_type: str, resource_id: int | str) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} with id={resource_id} not found.")


class InsufficientStockError(AppError):
    def __init__(
        self,
        product_id: int,
        product_name: str,
        requested: int,
        available: int,
    ) -> None:
        self.product_id = product_id
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product '{product_name}' (id={product_id}): "
            f"requested={requested}, available={available}."
        )


class InvalidStatusTransitionError(AppError):
    def __init__(self, current: str, requested: str) -> None:
        self.current = current
        self.requested = requested
        super().__init__(
            f"Cannot transition order status from '{current}' to '{requested}'."
        )


class ConflictError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
