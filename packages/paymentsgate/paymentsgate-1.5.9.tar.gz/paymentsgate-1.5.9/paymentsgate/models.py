from __future__ import annotations
import datetime
from decimal import Decimal
import json
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


from paymentsgate.enums import (
    Currencies,
    InvoiceTypes,
    Languages,
    Statuses,
    TTLUnits,
    CurrencyTypes,
    FeesStrategy,
    InvoiceDirection,
    CredentialsTypes,
)


class BaseRequestModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class BaseResponseModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Credentials(BaseModel):
    account_id: str
    public_key: str
    private_key: Optional[str] = Field(default=None)
    merchant_id: Optional[str] = Field(default=None)
    project_id: Optional[str] = Field(default=None)

    @classmethod
    def fromFile(cls, filename):
        data = json.load(open(filename))
        return cls(**data)

    model_config = ConfigDict(extra="ignore")


class PayInFingerprintBrowserModel(BaseRequestModel):
    acceptHeader: str
    colorDepth: int
    language: str
    screenHeight: int
    screenWidth: int
    timezone: str
    userAgent: str
    javaEnabled: bool
    windowHeight: int
    windowWidth: int


class PayInFingerprintModel(BaseRequestModel):
    fingerprint: str
    ip: str
    country: str
    city: str
    state: str
    zip: str
    browser: Optional[PayInFingerprintBrowserModel]


class PayInModel(BaseRequestModel):
    amount: float  # decimals: 2
    currency: Currencies
    country: Optional[str]  # Country iso code
    invoiceId: Optional[str]  # idempotent key
    clientId: Optional[str]  # uniq client ref
    type: InvoiceTypes  # Invoice subtype, see documentation
    bankId: Optional[str]  # ID from bank list or NSPK id
    trusted: Optional[bool]
    successUrl: Optional[str]
    failUrl: Optional[str]
    backUrl: Optional[str]
    clientCard: Optional[str]
    clientName: Optional[str]
    fingerprint: Optional[PayInFingerprintModel]
    lang: Optional[Languages]
    sync: Optional[bool]  # sync h2h scheme, see documentation
    multiWidgetOptions: Optional[PayInMultiWidgetOptions]
    theme: Optional[str]  # personalized widget theme


class PayInResponseModel(BaseResponseModel):
    id: str
    status: Statuses
    type: InvoiceTypes
    url: Optional[str]
    deeplink: Optional[str]
    m10: Optional[str]
    cardholder: Optional[str]
    account: Optional[str]
    bankId: Optional[str]
    accountSubType: Optional[str]


class PayOutRecipientModel(BaseRequestModel):
    account_number: str | None = None  #  IBAN, Phone, Card, local bank account number, wallet number, etc'
    account_owner: str | None = None  # FirstName LastName or FirstName MiddleName LastName
    account_iban: str | None = None  # use only cases where iban is't primary  account id
    account_swift: str | None = None  # for swift transfers only
    account_phone: str | None = None  # additional recipient phone number, use only cases where phone is't primary  account id
    account_bic: str | None = None  # recipient bank id
    account_ewallet_name: str | None = None  # additional recipient wallet provider info
    account_email: str | None = None  # additional recipient email, use only cases where email is't primary account id
    account_bank_id: str | None = None  # recipient bankId (from API banks or RU NSPK id)
    account_internal_client_number: str | None = None  # Bank internal identifier used for method banktransferphp (Philippines)
    type: CredentialsTypes | None = None  # primary credential type


class PayOutModel(BaseRequestModel):
    currency: Currencies | None = None  # currency from, by default = usdt
    currencyTo: Currencies | None = None  # currency to, fiat only, if use quoteId - not required
    amount: Decimal | None = None  # decimals: 2, if use quoteId - not required
    invoiceId: str | None = None  # idempotent key
    clientId: str | None = None  # uniq client ref
    ttl: int | None = None
    ttl_unit: TTLUnits | None = None
    finalAmount: Decimal | None = None  # Optional, for pre-charge rate lock
    sender_name: str | None = None  # sender personal short data
    sender_personal: PayOutSenderModel | None = None
    baseCurrency: CurrencyTypes | None = None
    feesStrategy: FeesStrategy | None = None
    recipient: PayOutRecipientModel
    quoteId: str | None = None
    src_amount: str | None = None  # Optional, source amount in local currency for 2phase payout
    type: InvoiceTypes | None = None  # payout transaction scheme hint


class PayOutResponseModel(BaseResponseModel):
    id: str
    status: str


class GetQuoteModel(BaseRequestModel):
    currency_from: Currencies
    currency_to: Currencies
    amount: Decimal
    subtype: InvoiceTypes | None = None
    currency_original: Currencies | None = None


class QuoteEntity(BaseResponseModel):
    currencyFrom: Currencies
    currencyTo: Currencies
    pair: str
    rate: float


class GetQuoteResponseModel(BaseResponseModel):
    id: str
    finalAmount: Decimal
    direction: InvoiceDirection
    fullRate: Decimal
    fullRateReverse: Decimal
    fees: Decimal
    fees_percent: Decimal
    quotes: List[QuoteEntity]
    expiredAt: Optional[datetime.datetime] | None = None

    # deprecated
    currency_from: Optional[CurrencyModel] = Field(default=None)
    currency_to: Optional[CurrencyModel] = Field(default=None)
    currency_middle: Optional[CurrencyModel] = Field(default=None)
    rate1: Optional[float] = Field(default=None)
    rate2: Optional[float] = Field(default=None)
    rate3: Optional[float] = Field(default=None)
    net_amount: Optional[float] = Field(default=None)
    metadata: Optional[object] = Field(default=None)


class DepositAddressResponseModel(BaseResponseModel):
    currency: Currencies
    address: str
    expiredAt: datetime.datetime


class CurrencyModel(BaseResponseModel):
    _id: str
    type: CurrencyTypes
    code: Currencies
    symbol: str
    label: Optional[str] = Field(default=None)
    decimal: int
    countryCode: Optional[str] = Field(default=None)
    countryName: Optional[str] = Field(default=None)


class BankModel(BaseResponseModel):
    name: str
    title: str
    currency: Currencies
    fpsId: str


class InvoiceStatusModel(BaseResponseModel):
    name: Statuses
    createdAt: datetime.datetime
    updatedAt: datetime.datetime


class InvoiceAmountModel(BaseResponseModel):
    crypto: float
    fiat: float
    fiat_net: float


class InvoiceMetadataModel(BaseResponseModel):
    invoiceId: Optional[str]  | None = None
    clientId: Optional[str]  | None = None
    fiatAmount: Optional[float]  | None = None


class InvoiceModel(BaseResponseModel):
    id: str | None = Field(..., alias='_id')
    orderId: str  | None = None
    projectId: str  | None = None
    currencyFrom: CurrencyModel  | None = None
    currencyTo: CurrencyModel  | None = None
    direction: InvoiceDirection  | None = None
    amount: float  | None = None
    status: InvoiceStatusModel  | None = None
    amounts: InvoiceAmountModel  | None = None
    metadata: InvoiceMetadataModel  | None = None
    receiptUrls: List[str]  | None = None
    isExpired: bool  | None = None
    createdAt: datetime.datetime | None = None
    updatedAt: datetime.datetime | None = None
    expiredAt: datetime.datetime | None = None
    model_config = ConfigDict(extra="ignore")


class AssetsAccountModel(BaseResponseModel):
    currency: CurrencyModel
    total: float
    pending: float
    available: float


class AssetsResponseModel(BaseResponseModel):
    assets: List[AssetsAccountModel]


class PayInMultiWidgetOptions(BaseRequestModel):
    offerAmount: Optional[bool]  # show amount select from best offers
    elqrBanks: Optional[str]  # elqr bank list


class PayOutSenderModel(BaseRequestModel):
    name: Optional[str]
    birthday: Optional[str]
    phone: Optional[str]
    passport: Optional[str]


class PayOutTlvRequestModel(BaseRequestModel):
    quoteId: str  # ID from /fx/tlv response
    invoiceId: Optional[str]
    clientId: Optional[str]
    sender_personal: Optional[PayOutSenderModel]


class GetQuoteTlv(BaseRequestModel):
    data: str

class TLVExtended(BaseResponseModel):
    merchant: str | None = None # MerchantName
    logo: str | None = None # MerchantLogo or merchant MCC logo
    city: str | None = None # Merchant city
    merchantId: str | None = None # uniq merchant id 
    zip: str | None = None # merchant address zip code
    qrRefId: str | None = None # uniq QR code reference id 
    invoiceId: str | None = None # Merchant invoiceId 
    merchantBank: str | None = None # Merchant bank name
    merchantIban: str | None = None # merchant iban
    merchantBankLogo: str | None = None # merchant bank logo

class QuoteTlvResponse(BaseResponseModel):
    id: str
    amount: float  # fiat local amount
    amountCrypto: float  # total crypto amount inc. fees
    currencyCode: Currencies  # local currency
    feeInCrypto: float  # total fee in crypto
    feePercent: float  # fee percent
    qrVersion: int  # qr code version, 1 - nspk, 2 - tlv encoded, 3 - tlv plain
    rate: float  # exchange rate
    tlv: TLVExtended | None = None
    isStatic: bool | None = None
    # merchant: Optional[str] = Field(default=None)  # merchant title
    # logo: Optional[str] = Field(default=None)  # merchant logo


class PayOutTlvRequest(BaseRequestModel):
    quoteId: str  # quote.id ref
    invoiceId: Optional[str] = Field(default=None)
    clientId: Optional[str] = Field(default=None)
    src_amount: Optional[float] = Field(default=None)
    sender_personal: Optional[PayOutSenderModel] = Field(default=None)

class ListMetadata(BaseResponseModel):
    page: int
    limit: int
    total: int

class InvoiceListModelWithMeta(BaseResponseModel): 
    meta: ListMetadata
    rows: List[InvoiceModel]
    model_config = ConfigDict(extra="ignore")