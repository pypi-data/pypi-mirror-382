from typing import Literal

LITERAL_ENVS = Literal[
    "internal-dev",
    "internal-dev-sandbox",
    "internal-qa",
    "internal-qa-sandbox",
    "ref",
    "dev",
    "int",
    "sandbox",
    "prod",
]

LITERAL_SECRET_TYPES = Literal[
    "apikey",
    "mtls"
]

PROXYGEN_CLIENT_ID = "proxygen-cli-user-client"
PROXYGEN_CLIENT_SECRET = "CDuV9K39GxFS37tzdopKitIMv8AZaIAj"
