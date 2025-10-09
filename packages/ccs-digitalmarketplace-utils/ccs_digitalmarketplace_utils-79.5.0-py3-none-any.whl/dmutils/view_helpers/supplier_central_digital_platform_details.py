import re

from ..govuk_country_register.country import to_country_from_json
from ..formats import nodaydateformat

ORGANISATION_SCEHME_TO_NAME = {
    'GB-COH': 'Companies House number',
    'GB-PPON': 'PPON',
    'GB-CHC': 'Charity Commission for England & Wales Number',
    'GB-SC': 'Scottish Charity Register',
    'GB-NIC': 'Charity Commission for Northern Ireland Number',
    'GB-MPR': 'Mutuals Public Register Number',
    'GG-RCE': 'Guernsey Registry Number',
    'JE-FSC': 'Jersey Financial Services Commission Registry Number',
    'IM-CR': 'Isle of Man Companies Registry Number',
    'GB-NHS': 'National Health Service Organisations Registry Number',
    'GB-UKPRN': 'UK Register of Learning Provider Number',
}

ORGANISATION_TYPE_TO_NAME = {
    'micro': 'Micro',
    'small': 'Small or medium-sized enterprise',
    'vcse': 'Non-governmental organisation',
    'shelteredWorkshop': 'Supported employment provider',
    'publicServiceMissionOrganization': 'Public service mutual',
    'other': 'My organisation is not defined'
}

ORGANISATION_FORM_TO_NAME = {
    'LimitedCompany': 'Limited company',
    'LLP': 'Limited liability partnership (LLP)',
    'LimitedPartnership': 'Limited partnership',
    'Other': 'Other'
}


def get_country_name_from_country_code(country_code):
    if country_code and country_code == 'gb':
        # We need to support the old country code style ('gb') until after the existing country code data we have in the
        # database has been updated by a script we'll run.
        # TODO: Remove support for old country codes after migration.
        return 'United Kingdom'

    if country_code:
        try:
            return to_country_from_json(country_code)
        except KeyError:
            return ''

    # In the case that a suppliers registration country isn't set we maintain existing behavior, which is for the
    # country to be returned as an empty string. 15/02/18
    return ''


def get_organisation_scheme_name(identifier):
    if identifier['scheme'] in ORGANISATION_SCEHME_TO_NAME:
        return ORGANISATION_SCEHME_TO_NAME[identifier['scheme']]

    if re.match(r'^[a-zA-Z]{2}-Other$', identifier['scheme']):
        country_name = get_country_name_from_country_code(f"country:{identifier['scheme'].split('-')[0]}")

        if country_name == '':
            return 'Other'

        return f'{country_name} - Other'

    return 'Other'


def organisation_scheme_mapper(identifier, additional_identifiers):
    identifiers = [{
        **identifier,
        'scheme_name': get_organisation_scheme_name(identifier)
    }]

    for additional_identifier in additional_identifiers:
        if bool(additional_identifier['id']) and additional_identifier['scheme'] != 'VAT':
            identifiers.append({
                **additional_identifier,
                'scheme_name': get_organisation_scheme_name(additional_identifier)
            })

    return identifiers


def get_organisation_type_listing(details):
    organisation_type = []

    if details['scale'] in ORGANISATION_TYPE_TO_NAME:
        organisation_type.append(ORGANISATION_TYPE_TO_NAME[details['scale']])

    for org_type in ['vcse', 'shelteredWorkshop', 'publicServiceMissionOrganization']:
        if details[org_type]:
            organisation_type.append(ORGANISATION_TYPE_TO_NAME[org_type])

    if len(organisation_type) == 0:
        organisation_type.append(ORGANISATION_TYPE_TO_NAME['other'])

    return '<br>'.join(organisation_type)


def get_organisation_legal_form(legal_form):
    organisation_legal_form = []

    if legal_form is None:
        return None

    if legal_form['registeredLegalForm'] in ORGANISATION_FORM_TO_NAME:
        organisation_legal_form.append(ORGANISATION_FORM_TO_NAME[legal_form['registeredLegalForm']])
    else:
        organisation_legal_form.append(legal_form['registeredLegalForm'])

    organisation_legal_form.append(legal_form['lawRegistered'])
    organisation_legal_form.append(nodaydateformat(f"{legal_form['registrationDate']}T12:00:00.000000Z"))

    return '<br>'.join(organisation_legal_form)
