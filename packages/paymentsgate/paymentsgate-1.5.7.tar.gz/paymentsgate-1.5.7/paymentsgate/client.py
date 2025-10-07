from __future__ import annotations
import logging

import json
from urllib.parse import urlencode
from pydantic import Field, BaseModel

from .types import TokenResponse
from .tokens import AccessToken, RefreshToken
from .exceptions import APIResponseError, APIAuthenticationError
from .models import (
    Credentials,
    GetQuoteModel,
    GetQuoteResponseModel,
    InvoiceListModelWithMeta,
    PayInModel,
    PayInResponseModel,
    PayOutModel,
    PayOutResponseModel,
    InvoiceModel,
    GetQuoteTlv,
    PayOutTlvRequest,
    QuoteTlvResponse,
)
from .enums import ApiPaths
from .transport import Request, Response
from .logger import Logger
from .cache import AbstractCache, DefaultCache

import httpx


class BaseClient:

    def __init__(self, config: Credentials, baseUrl: str, timeout: int = 20, debug: bool=False):
        self.config = config
        self.cache = DefaultCache()
        self.baseUrl = baseUrl
        self.timeout = timeout
        if debug:
            logging.basicConfig(level=logging.DEBUG)


class ApiAsyncClient(BaseClient):
    async def PayIn(self, request: PayInModel) -> PayInResponseModel:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.invoices_payin,
            content_type='application/json',
            noAuth=False,
            body=request.model_dump(exclude_none=True),
        )

        # Handle response
        response = await self._send_request(request)
        if (response.success):
            return response.cast(PayInResponseModel, APIResponseError)
        else:
            raise APIResponseError(response)

    async def PayOut(self, request: PayOutModel) -> PayOutResponseModel:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.invoices_payout,
            content_type='application/json',
            noAuth=False,
            signature=True,
            body=request.model_dump(exclude_none=True)
        )

        # Handle response
        response = await self._send_request(request)
        if (response.success):
            return response.cast(PayOutResponseModel, APIResponseError)
        else:
            raise APIResponseError(response)

    async def PayOutTlv(self, request: PayOutTlvRequest) -> PayOutResponseModel:
        request = Request(
            method="post",
            path=ApiPaths.invoices_payout_tlv,
            content_type="application/json",
            noAuth=False,
            signature=False,
            body=request.model_dump(exclude_none=True),
        )

        # Handle response
        response = await self._send_request(request)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(PayOutResponseModel, APIResponseError)

    async def Quote(self, params: GetQuoteModel) -> GetQuoteResponseModel:
         # Prepare request
        request = Request(
            method="get",
            path=ApiPaths.fx_quote,
            content_type='application/json',
            noAuth=False,
            signature=False,
            body=params.model_dump(exclude_none=True)
        )

        # Handle response
        response = await self._send_request(request)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(GetQuoteResponseModel, APIResponseError)

    async def QuoteQr(self, params: GetQuoteTlv) -> QuoteTlvResponse:
        request = Request(
            method="post",
            path=ApiPaths.fx_quote_tlv,
            content_type="application/json",
            noAuth=False,
            signature=False,
            body=params.model_dump(exclude_none=True),
        )

        # Handle response
        response = await self._send_request(request)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(QuoteTlvResponse, APIResponseError)

    async def Status(self, id: str) -> InvoiceModel:
         # Prepare request
        request = Request(
            method="get",
            path=ApiPaths.invoices_info.replace(':id', id),
            content_type='application/json',
            noAuth=False,
            signature=False,
        )

        # Handle response
        response = await self._send_request(request)
        if not response.success:
            raise APIResponseError(response)
        return response.cast(InvoiceModel, APIResponseError)
    
    async def List(self, page: int | int = 0) -> InvoiceListModelWithMeta:
         # Prepare request
        request = Request(
            method="get",
            path=ApiPaths.invoices_list.replace('$1', page | 10),
            content_type='application/json',
            noAuth=False,
            signature=False,
        )

        # Handle response
        response = await self._send_request(request)
        if not response.success:
            raise APIResponseError(response)
        return response.cast(InvoiceListModelWithMeta, APIResponseError)


    async def get_token(self) -> AccessToken | None:
        # First check if valid token is cached
        token = self.cache.get_token("AccessToken")
        refresh = self.cache.get_token("RefreshToken")

        if token is not None and not token.is_expired:
            return token
        else:
            # try to refresh token
            if refresh is not None and not refresh.is_expired:
                refreshed = await self._refresh_token(token, refresh)

                if refreshed.success:
                    access = AccessToken(refreshed.json_body["access_token"])
                    refresh = RefreshToken(
                        refreshed.json_body["refresh_token"],
                        int(refreshed.json_body["expires_in"]),
                    )

                    self.cache.set_token(access)
                    self.cache.set_token(refresh)

                    return access

            # try to issue token
            response = await self._fetch_token()
            if response.success:
                access = AccessToken(response.json_body["access_token"])
                refresh = RefreshToken(
                    response.json_body["refresh_token"],
                    int(response.json_body["expires_in"]),
                )

                self.cache.set_token(access)
                self.cache.set_token(refresh)

                return access
            else:
                raise APIAuthenticationError(response)

    async def _send_request(self, request: Request) -> Response:
        """
        Send a specified Request to the GoPay REST API and process the response
        """
        dict_factory = lambda l: {k: v for k, v in l if v is not None}
        body = request.body
        # Add Bearer authentication to headers if needed
        headers = request.headers or {}
        if not request.noAuth:
            auth = await self.get_token()
            if auth is not None:
                headers["Authorization"] = f"Bearer {auth.token}"

        client = httpx.AsyncClient(timeout=self.timeout)
        if request.method == 'get':
            url = f'{self.baseUrl}{request.path}'
            if body:
                params = urlencode(body)
                url = f'{url}?{params}'
            r = await client.request(
		        method=request.method,
                url=url,
                headers=headers,
                timeout=self.timeout
            )
        else:
            r = await client.request(
		        method=request.method,
 		        url=f"{self.baseUrl}{request.path}",
                headers=headers,
                json=body,
                timeout=self.timeout
            )

        # Build Response instance, try to decode body as JSON
        response = Response(raw_body=r.content, json={}, status_code=r.status_code)

        try:
            response.json_body = r.json()
        except json.JSONDecodeError:
            pass

        return response

    async def _fetch_token(self) -> Response:
        # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.token_issue,
            content_type='application/json',
            noAuth=True,
            body={"account_id": self.config.account_id, "public_key": self.config.public_key},
        )
        # Handle response
        response = await self._send_request(request)
        return response
    
    async def _refresh_token(self) -> Response:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.token_refresh,
            content_type='application/json',
            body={"refresh_token": self.refreshToken},
        )
        # Handle response
        response = await self._send_request(request)
        return response


class ApiClient(BaseClient):

    def PayIn(self, request: PayInModel) -> PayInResponseModel:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.invoices_payin,
            content_type='application/json',
            noAuth=False,
            body=request.model_dump(exclude_none=True),
        )

        # Handle response
        response = self._send_request(request)
        if (response.success):
            return response.cast(PayInResponseModel, APIResponseError)
        else:
            raise APIResponseError(response)
        
    def PayOut(self, request: PayOutModel) -> PayOutResponseModel:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.invoices_payout,
            content_type='application/json',
            noAuth=False,
            signature=True,
            body=request.model_dump(exclude_none=True)
        )

        # Handle response
        response = self._send_request(request)
        if (response.success):
            return response.cast(PayOutResponseModel, APIResponseError)
        else:
            raise APIResponseError(response)

    def PayOutTlv(self, request: PayOutTlvRequest) -> PayOutResponseModel:
        request = Request(
            method="post",
            path=ApiPaths.invoices_payout_tlv,
            content_type="application/json",
            noAuth=False,
            signature=False,
            body=request.model_dump(exclude_none=True),
        )

        # Handle response
        response = self._send_request(request)
        if not response.success:
            raise APIResponseError(response)
        return response.cast(PayOutResponseModel, APIResponseError)

    def Quote(self, params: GetQuoteModel) -> GetQuoteResponseModel:
         # Prepare request
        request = Request(
            method="get",
            path=ApiPaths.fx_quote,
            content_type='application/json',
            noAuth=False,
            signature=False,
            body=params.model_dump(exclude_none=True)
        )

        # Handle response
        response = self._send_request(request)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(GetQuoteResponseModel, APIResponseError)

    def QuoteQr(self, params: GetQuoteTlv) -> QuoteTlvResponse:
        request = Request(
            method="post",
            path=ApiPaths.fx_quote_tlv,
            content_type="application/json",
            noAuth=False,
            signature=False,
            body=params.model_dump(exclude_none=True),
        )

        # Handle response
        response = self._send_request(request)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(QuoteTlvResponse, APIResponseError)

    def Status(self, id: str) -> InvoiceModel:
         # Prepare request
        request = Request(
            method="get",
            path=ApiPaths.invoices_info.replace(':id', id),
            content_type='application/json',
            noAuth=False,
            signature=False,
        )

        # Handle response
        response = self._send_request(request)
        if not response.success:
            raise APIResponseError(response)

        return response.cast(InvoiceModel, APIResponseError)

    def get_token(self) -> AccessToken | None:
        # First check if valid token is cached
        token = self.cache.get_token('access')
        refresh = self.cache.get_token('refresh')
        if token is not None and not token.is_expired:
            return token
        else:
            # try to refresh token
            if refresh is not None and not refresh.is_expired:
                refreshed = self._refresh_token()

                if (refreshed.success):
                    access = AccessToken(
                        response.json_body["access_token"]
                    )
                    refresh = RefreshToken(
                        response.json_body["refresh_token"],
                        int(response.json_body["expires_in"]),
                    )
                    self.cache.set_token(access)
                    self.cache.set_token(refresh)

                    return access

            # try to issue token
            response = self._fetch_token()
            if response.success:
                
                access = AccessToken(
                    response.json_body["access_token"]
                )
                refresh = RefreshToken(
                    response.json_body["refresh_token"],
                    int(response.json_body["expires_in"]),
                )
                self.cache.set_token(access)
                self.cache.set_token(refresh)

                return access
            else:
                raise APIAuthenticationError(response)

    def _send_request(self, request: Request) -> Response:
        """
        Send a specified Request to the GoPay REST API and process the response
        """
        # Add Bearer authentication to headers if needed
        headers = request.headers or {}
        if not request.noAuth:
            auth = self.get_token()
            if auth is not None:
                headers["Authorization"] = f"Bearer {auth.token}"

        if (request.method == 'get'):
            params = urlencode(body)
            r = httpx.request(
                method=request.method,
                url=f"{self.baseUrl}{request.path}?{params}",
                headers=headers,
                timeout=self.timeout
            )
        else:
            r = httpx.request(
                method=request.method,
                url=f"{self.baseUrl}{request.path}",
                headers=headers,
                json=body,
                timeout=self.timeout
            )

        # Build Response instance, try to decode body as JSON
        response = Response(raw_body=r.content, json={}, status_code=r.status_code)

        try:
            response.json_body = r.json()
        except json.JSONDecodeError:
            pass
        return response

    def _fetch_token(self) -> Response:
        # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.token_issue,
            content_type='application/json',
            noAuth=True,
            body={"account_id": self.config.account_id, "public_key": self.config.public_key},
        )
        # Handle response
        response = self._send_request(request)
        return response

    def _refresh_token(self) -> Response:
         # Prepare request
        request = Request(
            method="post",
            path=ApiPaths.token_refresh,
            content_type='application/json',
            body={"refresh_token": self.refreshToken},
        )
        # Handle response
        response = self._send_request(request)
        return response
