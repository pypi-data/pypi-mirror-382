# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["Organization", "Address", "Contact"]


class Address(BaseModel):
    country: Optional[str] = None
    """The two character ISO 3166 country code.

    If none is provided, the organization's country code will be used.
    """

    line1: Optional[str] = None
    """The first line of the address, typically the number and street name"""

    line2: Optional[str] = None
    """
    The second line of the address if needed, typically an apartment or suite number
    """

    locality: Optional[str] = None
    """The city or locality"""

    name: Optional[str] = None
    """The name to which any mail should be addressed.

    If none is provided, this will default to the organization's registered_name
    """

    postal_code: Optional[str] = None
    """The postal code"""

    region: Optional[str] = None
    """The state or region"""


class Contact(BaseModel):
    email: Optional[str] = None
    """An email address at which the individual can be reached.

    Typically an email using the same domain name as the website URL will be
    preferred (e.g. with a website domain of `https://dtprecisionauto.com`, an email
    like `dom@dtprecisionauto.com` will be preferred over one like
    `dom@anothergarage.com` or `dom.toretto@gmail.com`)
    """

    first_name: Optional[str] = None
    """The first name (or given name) of the individual"""

    last_name: Optional[str] = None
    """The last name (or family name) of the individual"""

    phone_number: Optional[str] = None
    """A phone number at which the individual can be reached (E.164 format)"""

    title: Optional[Literal["ceo", "cfo", "director", "gm", "vp", "general_counsel", "other"]] = None
    """The job title of the individual."""

    title_other: Optional[str] = None
    """
    If `other` is provided for the `title` field, this field should be used to
    provide the title of the individual
    """


class Organization(BaseModel):
    address: Address
    """The address of the organization's headquarters."""

    contact: Contact
    """
    An object representing an individual who can be contacted if the carriers have
    any questions about the business.
    """

    country: Optional[str] = None
    """
    The two character ISO 3166 country code for the country in which the
    organization is headquartered.
    """

    email: Optional[str] = None
    """
    For publicly traded companies, an email for a representative of the company to
    whom a verification email will be sent. This must be an email on the same domain
    as the company's website (e.g. with a website domain of
    `https://dtprecisionauto.com`, the email must use the same
    `@dtprecisionauto.com`)
    """

    identifier: Optional[str] = None
    """The value of the identifier whose type is specified in the identifier_type
    field.

    Typically this will be an EIN, and can be formatted with or without the hyphen.
    """

    identifier_type: Optional[Literal["ein"]] = None
    """The type of identifier being provided for the organization.

    Support for more values will be added in the future.
    """

    industry: Optional[
        Literal[
            "agriculture",
            "automotive",
            "banking",
            "construction",
            "consumer",
            "education",
            "electronics",
            "energy",
            "engineering",
            "fast_moving_consumer_goods",
            "financial",
            "fintech",
            "food_and_beverage",
            "government",
            "healthcare",
            "hospitality",
            "insurance",
            "jewelry",
            "legal",
            "manufacturing",
            "media",
            "not_for_profit",
            "oil_and_gas",
            "online",
            "professional_services",
            "raw_materials",
            "real_estate",
            "religion",
            "retail",
            "technology",
            "telecommunications",
            "transportation",
            "travel",
        ]
    ] = None
    """The industry in which the organization operates."""

    mobile_number: Optional[str] = None
    """
    For sole proprietors, this must be a valid US mobile phone number to which a
    verification text message will be sent. (E.164 format)
    """

    regions_of_operation: Optional[
        List[Literal["africa", "asia", "australia", "europe", "latin_america", "usa_and_canada"]]
    ] = None
    """An array of regions in which the organization operates."""

    registered_name: Optional[str] = None
    """
    The legal name of the organization as registered with the IRS or other relevant
    authorities. For some applications, this will be matched against government
    records and should include all punctuation and everything else as well.
    """

    stock_exchange: Optional[
        Literal[
            "amex",
            "amx",
            "asx",
            "b3",
            "bme",
            "bse",
            "fra",
            "icex",
            "jpx",
            "jse",
            "krx",
            "lon",
            "nasdaq",
            "none",
            "nyse",
            "nse",
            "omx",
            "other",
            "sehk",
            "sgx",
            "sse",
            "sto",
            "swx",
            "szse",
            "tsx",
            "twse",
            "vse",
        ]
    ] = None
    """
    For publicly traded companies, this is the exchange on which the company's stock
    is traded.
    """

    stock_symbol: Optional[str] = None
    """For publicly traded companies, the ticker symbol for the company's stock"""

    type: Optional[
        Literal[
            "co_op",
            "government",
            "llc",
            "non_profit",
            "partnership",
            "private_corporation",
            "public_corporation",
            "sole_proprietor",
        ]
    ] = None
    """The type of organization"""

    website: Optional[str] = None
    """The URL of the website for this organization.

    The website should be publicly available, clearly reflect the organization's
    purpose, and the URL should start with `https://`
    """
