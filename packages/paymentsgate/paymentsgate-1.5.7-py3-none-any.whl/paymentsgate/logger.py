import logging
from paymentsgate.transport import Request, Response


def Logger(self, request: Request, response: Response):
    logging.debug(f"HTTP Request: {request}")
    logging.debug(f"HTTP Response: {response}")
