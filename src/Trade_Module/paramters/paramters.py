# Domains
DOMAIN_DEMAND = "Demand"
DOMAIN_EXPORT = "X"
DOMAIN_IMPORT = "M"
DOMAIN_PRODUCTION = "P"

DOMAIN_MAPPING = {
    "TransportationExport": DOMAIN_EXPORT,
    "TransportationImport": DOMAIN_IMPORT,
    "ManufactureCost": DOMAIN_PRODUCTION,
    "Supply": DOMAIN_PRODUCTION,
}

DOMAINS_TO_REMOVE = {
    DOMAIN_DEMAND,
}

# Data columns
GROUP_COLUMNS = [
    "Country",
    "Commodity",
    "domain",
    "Period",
]

LAG_GROUP_COLUMNS = [
    "Country",
    "Commodity",
    "domain",
]

INDEX_COLUMNS = [
    "Country",
    "Commodity",
    "Period",
]

VALUE_COLUMNS = [
    "p",
    "q",
]

COLUMN_MAPPING = {
    "price": "p",
    "quantity": "q",
    "CommodityCode": "Commodity",
}

COUNTRY_COLUMNS = [
    "Country",
    "Commodity",
    "Period",
    "P_p",
    "P_q",
    "M_p",
    "M_q",
    "X_p",
    "X_q",
]

PARTNER_COLUMNS = [
    "Country",
    "Commodity",
    "Period",
    "P_p",
    "P_q",
    "X_p",
    "X_q",
    "M_q",
]

# Countries per chunk size maybe changed if the RAM is smaller.
PROCESS_CHUNK_SIZE = 200