import os
import copy

from flask import current_app

from dmapiclient import CentralDigitalPlatformAPIClient


CENTRAL_DIGITAL_PLATFORM_DATA = {
    "id": "086a91ee-f448-4d7c-8b87-e2178521bc36",
    "name": "My Little Company",
    "associatedPersons": [],
    "additionalParties": [],
    "additionalEntities": [],
    "identifier": {
        "scheme": "GB-COH",
        "id": "12345678",
        "legalName": "My Little Registered Company",
        "uri": None,
    },
    "additionalIdentifiers": [
        {
            "scheme": "Other",
            "id": None,
            "legalName": "My Little Registered Company",
            "uri": None,
        },
        {
            "scheme": "GB-PPON",
            "id": "ELMA-1052-ICAM",
            "legalName": "My Little Registered Company",
            "uri": "https://supplier-information.com/organisations/ELMA-1052-ICAM",
        },
        {
            "scheme": "VAT",
            "id": "111222333",
            "legalName": "My Little Registered Company",
            "uri": None,
        },
    ],
    "address": {
        "streetAddress": "123 Fake Road",
        "locality": "Madeupolis",
        "region": None,
        "postalCode": "A11 1AA",
        "countryName": "United Kingdom",
        "country": "GB",
        "type": "Registered",
    },
    "contactPoint": {
        "name": None,
        "email": "mre@company.com",
        "telephone": None,
        "url": "https://www.mre.company",
    },
    "roles": ["tenderer"],
    "details": {
        "legalForm": {
            "registeredUnderAct2006": True,
            "registeredLegalForm": "LimitedCompany",
            "lawRegistered": "Companies Act 2006",
            "registrationDate": "2025-01-01",
        },
        "scale": "micro",
        "vcse": False,
        "shelteredWorkshop": False,
        "publicServiceMissionOrganization": False,
    },
    "supplierInformationData": {
        "form": {
            "name": "Standard Questions",
            "submissionState": "Submitted",
            "submittedAt": "2025-01-23T13:26:39.338624+00:00",
            "organisationId": "086a91ee-f448-4d7c-8b87-e2178521bc36",
            "formId": "9dfdde74-140e-4ce3-bea1-779be90d8e2a",
            "formVersionId": "1.0",
            "isRequired": True,
            "shareCode": "9LINliKU",
        },
        "answerSets": [
            {
                "id": "ae7fee3d-8a86-49b0-9f35-f082b94d38ea",
                "sectionName": "Qualifications",
                "answers": [],
            },
            {
                "id": "ca2621ef-e47d-4e12-9678-cfaef383d4fc",
                "sectionName": "Trade assurances",
                "answers": [],
            },
            {
                "id": "c0da4071-3d13-44cf-8e7e-6ccea5dda921",
                "sectionName": "Exclusions",
                "answers": [],
            },
            {
                "id": "afd061a6-ba46-45af-ae5e-7dce88994127",
                "sectionName": "Financial information",
                "answers": [
                    {
                        "questionName": "_FinancialInformation03",
                        "boolValue": True,
                        "numericValue": None,
                        "startValue": None,
                        "endValue": None,
                        "dateValue": None,
                        "textValue": None,
                        "optionValue": [],
                        "jsonValue": {},
                        "documentUri": None,
                    },
                    {
                        "questionName": "_FinancialInformation02",
                        "boolValue": None,
                        "numericValue": None,
                        "startValue": None,
                        "endValue": None,
                        "dateValue": None,
                        "textValue": None,
                        "optionValue": [],
                        "jsonValue": {},
                        "documentUri": "https://supplier-information.co/test_pdf_20250123132506219.pdf",
                    },
                    {
                        "questionName": "_FinancialInformation01",
                        "boolValue": None,
                        "numericValue": None,
                        "startValue": None,
                        "endValue": None,
                        "dateValue": "2024-03-31",
                        "textValue": None,
                        "optionValue": [],
                        "jsonValue": {},
                        "documentUri": None,
                    },
                ],
            },
        ],
        "questions": [
            {
                "type": "Text",
                "name": "_Qualifications01",
                "title": "Enter the qualification name",
                "text": '<div class="govuk-hint">Enter one qualification at a time. You can add another at the end if '
                "you need to. For example, ISO 45001 Health and Safety Management.</div>",
                "isRequired": True,
                "sectionName": "Qualifications",
                "options": [],
                "sortOrder": 1,
            },
            {
                "type": "Text",
                "name": "_Qualifications02",
                "title": "Who awarded the qualification?",
                "text": '<div class="govuk-hint">Enter the name of the person or body. For example, ISO, '
                "Constructionline or Red Tractor Assurance.</div>",
                "isRequired": True,
                "sectionName": "Qualifications",
                "options": [],
                "sortOrder": 2,
            },
            {
                "type": "Date",
                "name": "_Qualifications03",
                "title": "What date was the qualification awarded?",
                "text": "",
                "isRequired": True,
                "sectionName": "Qualifications",
                "options": [],
                "sortOrder": 3,
            },
            {
                "type": "Text",
                "name": "_TradeAssurance01",
                "title": "Who awarded the trade assurance?",
                "text": '<div class="govuk-hint">Enter the name of the person or body. You can add another at the end '
                "if you need to. For example, Red Tractor Assurance, QMS Assurance.</div>",
                "isRequired": True,
                "sectionName": "Trade assurances",
                "options": [],
                "sortOrder": 1,
            },
            {
                "type": "Text",
                "name": "_TradeAssurance02",
                "title": "Do you know the reference number?",
                "text": "",
                "isRequired": False,
                "sectionName": "Trade assurances",
                "options": [],
                "sortOrder": 2,
            },
            {
                "type": "Date",
                "name": "_TradeAssurance03",
                "title": "What date was the trade assurance awarded?",
                "text": "",
                "isRequired": True,
                "sectionName": "Trade assurances",
                "options": [],
                "sortOrder": 3,
            },
            {
                "type": "Boolean",
                "name": "_Exclusion07",
                "title": "Did this exclusion happen in the UK?",
                "text": "",
                "isRequired": True,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 1,
            },
            {
                "type": "Option",
                "name": "_Exclusion08",
                "title": "Select which exclusion applies",
                "text": '<div class="govuk-hint"><p>Only select one exclusion. You can add another at the end if you '
                "need to.</p><p>If this exclusion happened outside the UK, select the equivalent offence in "
                "the UK for where it took place.</p></div>",
                "isRequired": True,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 2,
            },
            {
                "type": "OptionJson",
                "name": "_Exclusion09",
                "title": "Select who the exclusion applies to",
                "text": '<div class="govuk-inset-text govuk-!-margin-top-0">If it applies to someone not listed, you '
                "must go back to the ‘Add a connected person’ section and add them.</div>",
                "isRequired": True,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 3,
            },
            {
                "type": "Text",
                "name": "_Exclusion06",
                "title": "Enter an email address",
                "text": '<div class="govuk-hint">Where the contracting authority can contact someone about the '
                "exclusion</div>",
                "isRequired": True,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 4,
            },
            {
                "type": "Text",
                "name": "_Exclusion05",
                "title": "Describe the exclusion in more detail",
                "text": '<div class="govuk-hint">Give us your explanation of the event. For example, any background '
                "information you can give about what happened or what caused the exclusion.</div>",
                "isRequired": True,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 5,
            },
            {
                "type": "Text",
                "name": "_Exclusion04",
                "title": "How the exclusion is being managed",
                "text": '<div class="govuk-hint"><p class="govuk-body">You must tell us what you or the person who was '
                'subject to the event:</p><ul class="govuk-list govuk-list--bullet"><li>have done to prove it '
                "was taken seriously - for example, paid a fine or compensation</li><li>have done to stop the "
                "circumstances that caused it from happening again - for example, taking steps like changing "
                "staff or management or putting procedures or training in place</li><li>are doing to monitor "
                "the steps that were taken - for example, regular meetings</li></ul></div>",
                "isRequired": True,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 6,
            },
            {
                "type": "FileUpload",
                "name": "_Exclusion03",
                "title": "Do you have a supporting document to upload?",
                "text": '<div id="documents-hint" class="govuk-hint">A decision from a public authority that was the '
                "basis for the offence. For example, documentation from the police, HMRC or the court.</div>",
                "isRequired": False,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 7,
            },
            {
                "type": "Url",
                "name": "_Exclusion10",
                "title": "Was the decision recorded on a public authority website?",
                "text": '<div class="govuk-hint">For example, the outcome of a court decision for a conviction or '
                "other event</div>",
                "isRequired": False,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 8,
            },
            {
                "type": "Date",
                "name": "_Exclusion02",
                "title": "Have the circumstances that led to the exclusion ended?",
                "text": '<div id="isEventEnded-hint" class="govuk-hint">For example, a court decision for '
                "environmental misconduct led your organisation or the connected person to stop harming the "
                "environment.</div>",
                "isRequired": False,
                "sectionName": "Exclusions",
                "options": [],
                "sortOrder": 9,
            },
            {
                "type": "Boolean",
                "name": "_FinancialInformation03",
                "title": "Were your accounts audited?",
                "text": "",
                "isRequired": True,
                "sectionName": "Financial information",
                "options": [],
                "sortOrder": 2,
            },
            {
                "type": "FileUpload",
                "name": "_FinancialInformation02",
                "title": "Upload your accounts",
                "text": '<p class="govuk-body">Upload your most recent 2 financial years. If you do not have 2, '
                "upload your most recent financial year.</p>",
                "isRequired": True,
                "sectionName": "Financial information",
                "options": [],
                "sortOrder": 3,
            },
            {
                "type": "Date",
                "name": "_FinancialInformation01",
                "title": "What is the financial year end date for the information you uploaded?",
                "text": "",
                "isRequired": True,
                "sectionName": "Financial information",
                "options": [],
                "sortOrder": 4,
            },
        ],
    },
}
SHARE_CODES_FOR_BYPASS = ['00000000', '11111111']


def get_dummy_central_digital_platform_data(
    supplier: dict,
    share_code: str,
    cdp_api_client: CentralDigitalPlatformAPIClient,
    disable_cdp_api: bool
):
    # Create and return a dummy CDP response data
    if (can_bypass_cdp := bypass_cdp(share_code)) or disable_cdp_api:
        supplier_id = supplier["id"]
        cdp_data: dict = copy.deepcopy(CENTRAL_DIGITAL_PLATFORM_DATA)

        if can_bypass_cdp:
            share_code = f'{cdp_data["supplierInformationData"]["form"]["shareCode"][:2]}{supplier_id}'

        if supplier.get('centralDigitalPlatformOrganisationId'):
            cdp_data["id"] = supplier['centralDigitalPlatformOrganisationId']
        else:
            cdp_data["id"] = f'{supplier_id}{cdp_data["id"][8:]}'

        registered_name = supplier.get("registeredName", supplier["name"])

        cdp_data["name"] = supplier["name"]
        cdp_data["identifier"]["legalName"] = registered_name
        cdp_data["identifier"]["id"] = f'{supplier_id}{cdp_data["identifier"]["id"][6:]}'

        for additional_identifier in cdp_data["additionalIdentifiers"]:
            additional_identifier["legalName"] = registered_name

        cdp_data["supplierInformationData"]["form"]["organisationId"] = cdp_data["id"]
        cdp_data["supplierInformationData"]["form"]["shareCode"] = share_code

        return cdp_data

    return cdp_api_client.get_supplier_submitted_information(share_code)


def is_cdp_api_disabled():
    return os.getenv("DM_ENVIRONMENT") != 'production' and current_app.config.get('DM_DISABLE_CDP_API', False) is True


def bypass_cdp(share_code):
    return os.getenv("DM_ENVIRONMENT") != 'production' and share_code in SHARE_CODES_FOR_BYPASS
