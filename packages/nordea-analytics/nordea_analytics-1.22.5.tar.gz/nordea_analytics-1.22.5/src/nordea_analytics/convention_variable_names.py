from enum import Enum


class DateRollConvention(Enum):
    """Date roll conventions available in the service."""

    Follow = "Follow"
    IMM_Wednesday = "IMM Wednesday"
    ModFollow = "Mod follow"
    NoDateRoll = "None"
    Preceeding = "Preceeding"
    StartOfMonthUnadjusted = "Start Of Month Unadjusted"


class DayCountConvention(Enum):
    """Day count conventions available in the service."""

    BankDays = "Bank Days"
    BusinessDays = "Business Days"
    CalendarDays = "Calendar Days"
    Days30 = "Days 30"
    Days30E = "Days 30E"
    Days30EP = "Days 30EP"


class SwapDayCountConvention(Enum):
    """Day count conventions available in the service."""

    ActAct = "act/act"
    ExaExa = "exa/exa"
    Act365 = "act/365"
    Act360 = "act/360"
    Bond = "30/360"
    Bond30E360 = "30e360"
    Bond30E360Isda = "30e360isda"
    BondBund = "bund"
    Isda360 = "30d360"
    Act36525 = "act/365.25"
    ActUst = "act/ust"
    ActActIcma = "act/act.icma"


class TimeConvention(Enum):
    """Time conventions available in the service."""

    TC_30360 = "30360"
    TC_30E360 = "30e360"
    TC_30EP360 = "30ep360"
    Act360 = "act360"
    Act365 = "act365"
    ISDAAct = "isdaact"
    ActNL365 = "actnl365"
    AFB = "afb"
    ActNL360 = "actnl360"


class Exchange(Enum):
    """Exchanges available in the service."""

    AmericanStockExchange = "AMEX"
    Amsterdam = "NLG"
    Ankara = "TRY"
    Athens = "GRD"
    AustralianStockExchange = "XASX"
    Bangkok = "THB"
    BelgradeStockExchange = "XBEL"
    BermudaStockExchange = "XBDA"
    BombayStockExchange = "XBOM"
    Bratislava = "SKK"
    BratislavaStockExchange = "XBRA"
    Brussel = "BEF"
    BucharestStockExchange = "RON"
    Budapest = "HUF"
    BudapestStockExchange = "XBUD"
    BulgarianStockExchange = "XBUL"
    CairoandAlexandriaStockExchange = "XCAI"
    CasablancaStockExchange = "XCAS"
    ColombiaStockExchange = "XBOG"
    Copenhagen = "DKK"
    CopenhagenOTC = "DKKOTC"
    CyprusStockExchange = "XCYS"
    Dublin = "IEP"
    Dusseldorf = "Dusseldorf"
    Frankfurt = "DEM"
    GhanaStockExchange = "XGHA"
    Helsinki = "FIM"
    HongKong = "HKD"
    HongKongStockExchange = "XHKG"
    IcelandStockExchange = "XICE"
    IndonesiaStockExchange = "XIDX"
    IstanbulStockExchange = "XIST"
    JohannesburgStockExchange = "XJSE"
    KarachiStockExchange = "XKAR"
    KievInternationalStockExchange = "XKIS"
    KoreanStockExchange = "XKRX"
    KuwaitStockExchange = "XKUW"
    LimaStockExchange = "XLIM"
    Lisbon = "PTE"
    LithuaniaStockExchange = "XLIT"
    Ljubljana = "SIT"
    London = "GBP"
    LondonStockExchange = "XLON"
    Luxembourg = "LUF"
    Madrid = "ESP"
    MexicoCity = "MXN"
    MexicoStockExchange = "XMEX"
    Milano = "ITL"
    Montreal = "Montreal"
    Moscow = "RUB"
    MoscowStockExchange = "XMOS"
    NagoyaStockExchange = "XNGO"
    NasdaqOTC = "Nasdaq OTC"
    NationalStockExchangeofIndia = "XNSE"
    NewYork = "USD"
    NewYorkStockExchange = "XNYS"
    NewZealandStockExchange = "XNZE"
    NigerianStockExchange = "XNSA"
    OsakaStockExchange = "XOSE"
    Oslo = "NOK"
    Paris = "FRF"
    PhilippineStockExchange = "XPHS"
    Prague = "CZK"
    PragueStockExchange = "XPRA"
    Reykjavik = "ISK"
    Riga = "LVL"
    RigaStockExchange = "XRIS"
    Riyadh = "SAR"
    SantiagoStockExchange = "XSGO"
    SaudiArabianStockExchange = "XSAU"
    ShanghaiStockExchange = "XSHG"
    Singapore = "SGD"
    SingaporeExchange = "XSES"
    Stockholm = "SEK"
    SwissExchange = "XSWX"
    Sydney = "AUD"
    TaiwanStockExchange = "XTAI"
    Tallinn = "EEK"
    TallinnStockExchange = "XTAL"
    Target = "EUR"
    TehranStockExchange = "XTEH"
    TelAviv = "ILS"
    TelAvivStockExchange = "XTAE"
    ThailandStockExchange = "XBKK"
    Tokyo = "JPY"
    TokyoStockExchange = "XTKS"
    Toronto = "Toronto"
    TorontoStockExchange = "XTSE"
    Vienna = "ATS"
    Vilnius = "LTL"
    Warsaw = "PLN"
    WarsawStockExchange = "XWAR"
    Wellington = "NZD"
    XETRAStockExchange = "XETRA"
    Zagreb = "HRK"
    ZagrebStockExchange = "XZAG"
    Zurich = "CHF"


class CashflowType(Enum):
    """Cashflow types available in the service."""

    CSE = "CSE"
    MCI = "MCI"


class DmbModel(Enum):
    """DMB models available in the service."""

    Current = "current"
    Before2024 = "before2024"


class SwapLegType(Enum):
    """Swap leg types available in the service."""

    Fixed = "fixed"
    Floating = "floating"


class SwapFixingFrequency(Enum):
    """Swap fixing frequencies available in the service."""

    OIS = "1D"
    RFR = "RFR"
    Quarterly = "3M"
    SemiAnnually = "6M"
