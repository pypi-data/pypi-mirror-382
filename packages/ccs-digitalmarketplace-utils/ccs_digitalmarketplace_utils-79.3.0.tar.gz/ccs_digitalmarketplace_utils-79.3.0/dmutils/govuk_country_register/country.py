
from .register import CSVRegister, JSONRegister


def __load_csv__():
    return CSVRegister.from_pkg_resource("country.csv")


def __load_json__():
    return JSONRegister.from_pkg_resource("country.json")


csv_register = __load_csv__()
json_register = __load_json__()


def to_country(country_code):
    """Find the name for a country from its two-letter country code

    :param country_code str:  the two-letter country code
    :return str:  the country's commonly-used name in English

    The country codes used are two-letter ISO 3166-2 alpha-2 codes,
    which are also typically used as a country's top-level domain on the
    internet.

    The data is drawn from GOV.UK's country register at
    https://www.registers.service.gov.uk/registers/country.
    """

    return csv_register.find(country_code)["name"]


def to_country_from_json(country_code):
    """Find the name for a country from its two-letter country code and type

    :param country_code str:  the two-letter country code
    :return str:  the country's commonly-used name in English
    """

    return json_register.find(country_code)
