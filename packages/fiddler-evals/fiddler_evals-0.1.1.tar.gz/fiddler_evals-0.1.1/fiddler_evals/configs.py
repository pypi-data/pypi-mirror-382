from decouple import config

REQUEST_CONN_TIMEOUT_SECONDS = config(
    "FIDDLER_REQUEST_CONNECTION_TIMEOUT_SECONDS", cast=int, default=5
)
REQUEST_READ_TIMEOUT_SECONDS = config(
    "FIDDLER_REQUEST_READ_TIMEOUT_SECONDS", cast=int, default=10
)

# requests lib format (conn. timeout, read timeout)
REQUEST_TIMEOUT_SECONDS = (REQUEST_CONN_TIMEOUT_SECONDS, REQUEST_READ_TIMEOUT_SECONDS)


REQUEST_PAGE_SIZE = config("FIDDLER_REQUEST_PAGE_SIZE", cast=int, default=50)
