from paymentsgate.transport import Response


class PaymentsgateError(Exception):
    pass


class APIError(PaymentsgateError):
    error: str
    message: str
    code: int
    data: object | None
    details: object | None

    def __init__(
        self,
        error: str,
        message: str,
        data: object | None,
        details: object | None,
        status: int,
    ) -> None:
        super().__init__(f"[{error}] {message} (status: {status})")
        self.error = error
        self.message = message
        self.data = data
        self.code = status
        self.details = details
        if details is not None:
            print("Error details:", self.details)
        if data is not None:
            print(self.data)
        # print(f"{self.error}: {self.message} code: {self.code} details: {self.details}")


class APIResponseError(APIError):
    def __init__(self, response: Response) -> None:
        super().__init__(
            response.json_body.get("error"),
            response.json_body.get("message"),
            response.json_body.get("data"),
            response.json_body.get("details"),
            response.status_code,
        )


class APIAuthenticationError(APIError):
    def __init__(self, response: Response) -> None:
        super().__init__(
            response.json_body.get("error"),
            response.json_body.get("message"),
            response.json_body.get("data"),
            response.json_body.get("details"),
            response.status_code,
        )
