from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar, Union
from maleo.types.string import ListOfStrings


class Scheme(StrEnum):
    HTTP = "http"
    HTTPS = "https"
    WS = "ws"
    WSS = "wss"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


SchemeT = TypeVar("SchemeT", bound=Scheme)
OptionalScheme = Optional[Scheme]
OptionalSchemeT = TypeVar("OptionalSchemeT", bound=OptionalScheme)
ListOfSchemes = List[Scheme]
ListOfSchemesT = TypeVar("ListOfSchemesT", bound=ListOfSchemes)
OptionalListOfSchemes = Optional[ListOfSchemes]
OptionalListOfSchemesT = TypeVar("OptionalListOfSchemesT", bound=OptionalListOfSchemes)
SequenceOfSchemes = Sequence[Scheme]
SequenceOfSchemesT = TypeVar("SequenceOfSchemesT", bound=SequenceOfSchemes)
OptionalSequenceOfSchemes = Optional[SequenceOfSchemes]
OptionalSequenceOfSchemesT = TypeVar(
    "OptionalSequenceOfSchemesT", bound=OptionalSequenceOfSchemes
)


class Protocol(StrEnum):
    HTTP = "http"
    WEBSOCKET = "websocket"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]

    @classmethod
    def from_scheme(cls, scheme: Union[Scheme, str]) -> "Protocol":
        # Normalize to Scheme if it's a string
        if isinstance(scheme, str):
            try:
                scheme = Scheme(scheme)
            except ValueError:
                raise ValueError(f"Unknown scheme: {scheme}")

        if scheme in (Scheme.HTTP, Scheme.HTTPS):
            return cls.HTTP
        elif scheme in (Scheme.WS, Scheme.WSS):
            return cls.WEBSOCKET
        raise ValueError(f"Unknown scheme: {scheme}")


class Method(StrEnum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


MethodT = TypeVar("MethodT", bound=Method)
OptionalMethod = Optional[Method]
OptionalMethodT = TypeVar("OptionalMethodT", bound=OptionalMethod)
ListOfMethods = List[Method]
ListOfMethodsT = TypeVar("ListOfMethodsT", bound=ListOfMethods)
OptionalListOfMethods = Optional[ListOfMethods]
OptionalListOfMethodsT = TypeVar("OptionalListOfMethodsT", bound=OptionalListOfMethods)
SequenceOfMethods = Sequence[Method]
SequenceOfMethodsT = TypeVar("SequenceOfMethodsT", bound=SequenceOfMethods)
OptionalSequenceOfMethods = Optional[SequenceOfMethods]
OptionalSequenceOfMethodsT = TypeVar(
    "OptionalSequenceOfMethodsT", bound=OptionalSequenceOfMethods
)


class Header(StrEnum):
    # --- Authentication & Authorization ---
    AUTHORIZATION = "authorization"
    PROXY_AUTHORIZATION = "proxy-authorization"
    WWW_AUTHENTICATE = "www-authenticate"

    # --- Content & Caching ---
    CACHE_CONTROL = "cache-control"
    CONTENT_DISPOSITION = "content-disposition"
    CONTENT_ENCODING = "content-encoding"
    CONTENT_LENGTH = "content-length"
    CONTENT_TYPE = "content-type"
    ETAG = "etag"
    LAST_MODIFIED = "last-modified"
    EXPIRES = "expires"
    VARY = "vary"

    # --- Client & Request Context ---
    ACCEPT = "accept"
    ACCEPT_ENCODING = "accept-encoding"
    ACCEPT_LANGUAGE = "accept-language"
    ACCEPT_CHARSET = "accept-charset"
    HOST = "host"
    ORIGIN = "origin"
    REFERER = "referer"
    USER_AGENT = "user-agent"

    # --- Range / Conditional Requests ---
    RANGE = "range"
    CONTENT_RANGE = "content-range"
    IF_MATCH = "if-match"
    IF_NONE_MATCH = "if-none-match"
    IF_MODIFIED_SINCE = "if-modified-since"
    IF_UNMODIFIED_SINCE = "if-unmodified-since"

    # --- Correlation / Observability ---
    X_COMPLETED_AT = "x-completed-at"
    X_CONNECTION_ID = "x-connection-id"
    X_DURATION = "x-duration"
    X_EXECUTED_AT = "x-executed-at"
    X_OPERATION_ID = "x-operation-id"
    X_TRACE_ID = "x-trace-id"
    X_SPAN_ID = "x-span-id"

    # --- Organization / User Context ---
    X_ORGANIZATION_ID = "x-organization-id"
    X_USER_ID = "x-user-id"

    # --- API Keys / Clients ---
    X_API_KEY = "x-api-key"
    X_CLIENT_ID = "x-client-id"
    X_CLIENT_SECRET = "x-client-secret"
    X_SIGNATURE = "x-signature"

    # --- Cookies & Sessions ---
    COOKIE = "cookie"
    SET_COOKIE = "set-cookie"

    # --- Redirects & Responses ---
    LOCATION = "location"
    ALLOW = "allow"
    RETRY_AFTER = "retry-after"
    LINK = "link"

    # --- Proxy / Networking ---
    FORWARDED = "forwarded"
    X_FORWARDED_FOR = "x-forwarded-for"
    X_FORWARDED_PROTO = "x-forwarded-proto"
    X_FORWARDED_HOST = "x-forwarded-host"
    X_FORWARDED_PORT = "x-forwarded-port"
    X_REAL_IP = "x-real-ip"

    # --- Security ---
    STRICT_TRANSPORT_SECURITY = "strict-transport-security"
    CONTENT_SECURITY_POLICY = "content-security-policy"
    X_FRAME_OPTIONS = "x-frame-options"
    X_CONTENT_TYPE_OPTIONS = "x-content-type-options"
    REFERRER_POLICY = "referrer-policy"
    PERMISSIONS_POLICY = "permissions-policy"

    # --- Experimental / Misc ---
    X_NEW_AUTHORIZATION = "x-new-authorization"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


HeaderT = TypeVar("HeaderT", bound=Header)
OptionalHeader = Optional[Header]
OptionalHeaderT = TypeVar("OptionalHeaderT", bound=OptionalHeader)
ListOfHeaders = List[Header]
ListOfHeadersT = TypeVar("ListOfHeadersT", bound=ListOfHeaders)
OptionalListOfHeaders = Optional[ListOfHeaders]
OptionalListOfHeadersT = TypeVar("OptionalListOfHeadersT", bound=OptionalListOfHeaders)
SequenceOfHeaders = Sequence[Header]
SequenceOfHeadersT = TypeVar("SequenceOfHeadersT", bound=SequenceOfHeaders)
OptionalSequenceOfHeaders = Optional[SequenceOfHeaders]
OptionalSequenceOfHeadersT = TypeVar(
    "OptionalSequenceOfHeadersT", bound=OptionalSequenceOfHeaders
)
