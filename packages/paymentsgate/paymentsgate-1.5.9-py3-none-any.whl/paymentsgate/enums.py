from enum import StrEnum


class AuthenticationRealms(StrEnum):
    production = "production"
    sandbox = "sandbox"


class ApiPaths(StrEnum):
    token_issue = "/auth/token"
    token_refresh = "/auth/token/refresh"
    token_revoke = "/auth/token/revoke"
    token_validate = "/auth/token/validate"
    invoices_payin = "/deals/payin"
    invoices_payout = "/deals/payout"
    invoices_payout_tlv = "/deals/tlv"
    invoices_info = "/deals/:id"
    invoices_credentials = "/deals/:id/credentials"
    invoices_list = "/deals/list"
    assets_list = "/wallet"
    assets_deposit = "/wallet/deposit"
    banks_list = "/banks/find"
    appel_create = "/support/create"
    appel_list = "/support/list"
    appel_stat = "/support/statistic"
    fx_quote = "/fx/calculatenew"
    fx_quote_tlv = "/fx/tlv"


class Currencies(StrEnum):
    USDT = "USDT"
    RUB = "RUB"
    EUR = "EUR"
    USD = "USD"
    TRY = "TRY"
    BYN = "BYN"
    CNY = "CNY"
    JPY = "JPY"
    GEL = "GEL"
    AZN = "AZN"
    INR = "INR"
    AED = "AED"
    KZT = "KZT"
    UZS = "UZS"
    TJS = "TJS"
    EGP = "EGP"
    PKR = "PKR"
    IDR = "IDR"
    BDT = "BDT"
    GBP = "GBP"
    THB = "THB"
    KGS = "KGS"
    PHP = "PHP"
    ZAR = "ZAR"
    ARS = "ARS"
    GHS = "GHS"
    KES = "KES"
    NGN = "NGN"
    AMD = "AMD"
    XOF = "XOF"
    CAD = "CAD"
    AFN = "AFN"
    ALL = "ALL"
    AUD = "AUD"
    BAM = "BAM"
    BGN = "BGN"
    BHD = "BHD"
    BIF = "BIF"
    BND = "BND"
    BOB = "BOB"
    BRL = "BRL"
    BWP = "BWP"
    BZD = "BZD"
    CDF = "CDF"
    CHF = "CHF"
    CLP = "CLP"
    COP = "COP"
    CRC = "CRC"
    CVE = "CVE"
    CZK = "CZK"
    DJF = "DJF"
    DKK = "DKK"
    DOP = "DOP"
    DZD = "DZD"
    EEK = "EEK"
    ERN = "ERN"
    ETB = "ETB"
    GNF = "GNF"
    GTQ = "GTQ"
    HKD = "HKD"
    HNL = "HNL"
    HRK = "HRK"
    HUF = "HUF"
    ILS = "ILS"
    IQD = "IQD"
    IRR = "IRR"
    ISK = "ISK"
    JMD = "JMD"
    JOD = "JOD"
    KHR = "KHR"
    KMF = "KMF"
    KRW = "KRW"
    KWD = "KWD"
    LBP = "LBP"
    LKR = "LKR"
    LTL = "LTL"
    LVL = "LVL"
    LYD = "LYD"
    MAD = "MAD"
    MDL = "MDL"
    MGA = "MGA"
    MKD = "MKD"
    MMK = "MMK"
    MOP = "MOP"
    MUR = "MUR"
    MXN = "MXN"
    MYR = "MYR"
    MZN = "MZN"
    NAD = "NAD"
    NIO = "NIO"
    NOK = "NOK"
    NPR = "NPR"
    NZD = "NZD"
    OMR = "OMR"
    PAB = "PAB"
    PEN = "PEN"
    PLN = "PLN"
    PYG = "PYG"
    QAR = "QAR"
    RON = "RON"
    RSD = "RSD"
    RWF = "RWF"
    SAR = "SAR"
    SDG = "SDG"
    SEK = "SEK"
    SGD = "SGD"
    SOS = "SOS"
    SYP = "SYP"
    TND = "TND"
    TOP = "TOP"
    TTD = "TTD"
    TWD = "TWD"
    TZS = "TZS"
    UAH = "UAH"
    UGX = "UGX"
    UYU = "UYU"
    VEF = "VEF"
    VND = "VND"
    YER = "YER"
    ZMK = "ZMK"
    MNT = "MNT"

class Languages(StrEnum):
    EN = ("EN",)
    AZ = ("AZ",)
    UZ = ("UZ",)
    GE = ("GE",)
    TR = ("TR",)
    AE = ("AE",)
    RU = ("RU",)
    IN = ("IN",)
    AR = ("AR",)
    KG = "KG"


class Statuses(StrEnum):
    queued = "queued"
    new = "new"
    pending = "pending"
    paid = "paid"
    completed = "completed"
    disputed = "disputed"
    canceled = "canceled"
    expired = "expired"


class CurrencyTypes(StrEnum):
    fiat = "FIAT"
    crypto = "CRYPTO"


class InvoiceTypes(StrEnum):
  p2p = ("p2p",)
  c2c = ("c2c",)
  m10 = ("m10",)
  mpay = ("mpay",)
  sbp = ("sbp",)
  sbpqr = ("sbpqr",)
  iban = ("iban",)
  upi = ("upi",)
  imps = ("imps",)
  spei = ("spei",)
  pix = ("pix",)
  rps = ("rps",)
  ibps = ("ibps",)
  bizum = ("bizum",)
  rkgs = ("rkgs",)
  kgsphone = ("kgsphone",)
  krungthainext = ("krungthainext",)
  sber = ("sber",)
  kztphone = ("kztphone",)
  bkash = ("bkash",)
  nagad = ("nagad",)
  alipay = ("alipay",)
  accountegp = ("accountegp",)
  accountphp = ("accountphp",)
  sberqr = ("sberqr",)
  maya = ("maya",)
  gcash = ("gcash",)
  banktransferphp = ("banktransferphp",)
  banktransferars = ("banktransferars",)
  phonepe = ("phonepe",)
  freecharge = ("freecharge",)
  instapay = ("instapay",)
  vodafonecash = ("vodafonecash",)
  orangecash = ("orangecash",)
  razn = ("razn",)
  rtjs = ("rtjs",)
  skzt = ("skzt",)
  scny = ("scny",)
  vtbcny = ("vtbcny",)
  sgel = ("sgel",)
  seur = ("seur",)
  stry = ("stry",)
  sthb = ("sthb",)
  sberpay = ("sberpay",)
  tpay = ("tpay",)
  opay = ("opay",)
  moniepoint = ("moniepoint",)
  palmpay = ("palmpay",)
  wave = ("wave",)
  orangemoney = ("orangemoney",)
  moovmoney = ("moovmoney",)
  rtjscard = ("rtjscard",)
  ruzs = ("ruzs",)
  amobile = ("amobile",)
  payid = ("payid",)
  baridi = ("baridi",)
  multiwidget = ("multiwidget",)
  banktransfermad = ("banktransfermad",)
  cih = ("cih",)
  cashplus = ("cashplus",)
  elqr = ("elqr",)
  odengi = ("odengi",)
  banktransferdop = ("banktransferdop",)
  sinpemovil = ("sinpemovil",)
  tryqr = ("tryqr",)
  inrqr = ("inrqr",)
  bsb = ("bsb",)
  banktransfermnt = ("banktransfermnt",)
  stcpay = ("stcpay",)
  upiqr = ("upiqr",)
  ifsc = ("ifsc",)
  tjsbank = ("tjsbank",)
  sortgbp = ("sortgbp",)
  unionpay = ("unionpay",)
  ecomazn = ("ecomazn",)
  ecomrub = ("ecomrub",)
  banktransferthb = ("banktransferthb",)
  banktransferzar = ("banktransferzar",)
  dcecomusd = ("dcecomusd",)
  dcecomeur = ("dcecomeur",)
  benefitpay = "benefitpay"

class EELQRBankALias(StrEnum):
    bakai = ("bakai",)
    mbank = ("mbank",)
    optima = ("optima",)
    kicb = ("kicb",)
    odengi = ("odengi",)
    demir = ("demir",)
    megapay = "megapay"


class CredentialsTypes(StrEnum):
    iban = ("iban",)
    phone = ("phone",)
    card = ("card",)
    fps = ("fps",)
    qr = ("qr",)
    account = ("account",)
    custom = "custom"


class RiskScoreLevels(StrEnum):
    unclassified = "unclassified"
    hr = "hr"  # highest risk
    ftd = "ftd"  # high risk
    trusted = "trusted"  # low risk


class CancellationReason(StrEnum):
    NO_MONEY = ("NO_MONEY",)
    CREDENTIALS_INVALID = ("CREDENTIALS_INVALID",)
    EXPIRED = ("EXPIRED",)
    PRECHARGE_GAP_UPPER_LIMIT = ("PRECHARGE_GAP_UPPER_LIMIT",)
    CROSS_BANK_TFF_LESS_THAN_3K = ("CROSS_BANK_TFF_LESS_THAN_3K",)
    CROSS_BANK_UNSUPPORTED = ("CROSS_BANK_UNSUPPORTED",)
    ACCOUNT_NUMBER_BLACKLISTED = ("ACCOUNT_NUMBER_BLACKLISTED",)
    ANTISPAM = ("ANTISPAM",)
    BY_CLIENT = ("BY_CLIENT",)
    BY_EXPIRATION = ("BY_EXPIRATION",)
    PAID_CANCEL_BY_EXPIRATION = "PAID_BY_EXPIRATION"


class FeesStrategy(StrEnum):
    add = "add"
    sub = "sub"


class InvoiceDirection(StrEnum):
    F2C = ("F2C",)
    C2F = ("C2F",)
    FIAT_IN = ("FIAT_IN",)
    FIAT_OUT = "FIAT_OUT"


class TTLUnits(StrEnum):
    sec = "sec"
    min = "min"
    hour = "hour"
