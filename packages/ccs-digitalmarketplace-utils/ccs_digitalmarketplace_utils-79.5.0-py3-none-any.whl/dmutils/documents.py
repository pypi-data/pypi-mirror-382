import os
import datetime
import re

import fleep
import urllib.parse as urlparse

from .s3 import S3ResponseError, get_file_size


BAD_SUPPLIER_NAME_CHARACTERS = ['#', '%', '&', '{', '}', '\\', '<', '>', '*', '?', '/', '$',
                                '!', "'", '"', ':', '@', '+', '`', '|', '=', ',', '.']

RESULT_LETTER_FILENAME = 'result-letter.pdf'

AGREEMENT_FILENAME = 'framework-agreement.pdf'
SIGNED_AGREEMENT_PREFIX = 'signed-framework-agreement'

SIGNATURE_PAGE_FILENAME = 'signature-page.pdf'
SIGNED_SIGNATURE_PAGE_PREFIX = 'signed-signature-page'

COUNTERPART_FILENAME = "agreement-countersignature.pdf"

ONE_MEGABYTE_IN_BYTES = 1_048_576


def filter_empty_files(files):
    """Remove any empty files from the list.

    :param files: a dictionary of file attachments
    :return: a dictionary of files with all empty files removed

    """
    return {
        key: contents for key, contents in files.items()
        if file_is_not_empty(contents)
    }


def file_is_open_document_format(file_object):
    extension = get_extension(file_object.filename)

    return (
        extension in [".pdf", ".odt", ".ods", ".odp"]
        and extension_matches_possible_file_formats(file_object, extension)
    )


def file_is_spreadsheet_format(file_object):
    """Checks file extension and format as being ods."""
    extension = get_extension(file_object.filename)

    return (
        extension in [".ods", ".xlsx"]
        and extension_matches_possible_file_formats(file_object, extension)
    )


def file_is_docx(file_object):
    extension = get_extension(file_object.filename)

    return (
        extension == ".docx"
        and extension_matches_possible_file_formats(file_object, extension)
    )


def file_is_pdf(file_object):
    """Checks file extension and format as being PDF."""
    extension = get_extension(file_object.filename)

    return extension == ".pdf" and extension_matches_possible_file_formats(file_object, extension)


def file_is_csv(file_object):
    """Checks file extension as being CSV and checks format does not match something other than CSV."""
    extension = get_extension(file_object.filename)

    return extension == ".csv" and get_possible_extensions_from_format(file_object) == []


def file_is_zip(file_object):
    """Checks file extension and format as being ZIP."""
    extension = get_extension(file_object.filename)

    return extension == ".zip" and extension_matches_possible_file_formats(file_object, extension)


def file_is_image(file_object):
    """Checks file extension and format as being JPG. or PNG. JPEG is normalised to JPG"""
    extension = get_extension(file_object.filename)
    extension = extension if extension != '.jpeg' else '.jpg'

    return extension in [".jpg", ".png"] and extension_matches_possible_file_formats(file_object, extension)


FILE_TYPE_TO_VALIDATION = {
    'open_document': file_is_open_document_format,
    'spreadsheet': file_is_spreadsheet_format,
    'pdf': file_is_pdf,
    'csv': file_is_csv,
    'zip': file_is_zip,
    'image': file_is_image,
    'docx': file_is_docx,
}


def validate_documents(files, section):
    errors = {}

    for field, contents in files.items():
        question = section.get_question(field)

        validators = [
            FILE_TYPE_TO_VALIDATION.get(file_type)
            for file_type in question.file_settings['file_types']
        ]

        if not any(validator(contents) for validator in validators):
            errors[field] = 'file_is_valid_format'
        elif not file_is_less_than_n_mb(contents, question.file_settings['max_size']):
            errors[field] = f"file_is_less_than_{question.file_settings['max_size']}mb"

    return errors


def upload_document(
    uploader,
    upload_type,
    documents_url,
    service,
    filename_suffix,
    file_contents,
    item_number=None,
    public=True
):
    """Upload the document to S3 bucket and return the document URL

    :param uploader: S3 uploader object
    :param upload_type: Upload type (eg 'documents' or 'submissions')
    :param documents_url: base assets URL used as root for creating the full
                          document URL.
    :param service: service object used to look up service and supplier id
                    for the generated document name
    :param field: name of the service field that the document URL is saved to,
                  used to generate the document name
    :param file_contents: attached file object
    :param public: if True, set file permission to 'public-read'. Otherwise 'bucket-owner-full-control',
                   which is private to the object owner and bucket owner.

    :return: generated document URL or ``False`` if document upload
             failed

    """
    if upload_type not in ('documents', 'submissions',):
        raise ValueError(f"Unexpected upload_type {upload_type!r}")

    file_path = generate_file_name(
        service['frameworkSlug'],
        upload_type,
        service['supplierId'],
        filename_suffix,
        file_contents.filename,
        service_id=service.get('id'),
        item_number=item_number,
    )

    acl = 'public-read' if public else 'bucket-owner-full-control'

    try:
        uploader.save(file_path, file_contents, acl=acl)
    except S3ResponseError:
        return False

    full_url = urlparse.urljoin(
        documents_url,
        file_path
    )

    return full_url


def upload_service_documents(
    uploader,
    upload_type,
    documents_url,
    service,
    request_files,
    section,
    item_number=None,
    public=True
):
    if upload_type not in ('documents', 'submissions',):
        raise ValueError(f"Unexpected upload_type {upload_type!r}")

    files = {
        field: request_files[field]
        for field in section.get_question_ids(type="upload")
        if field in request_files
    }
    files = filter_empty_files(files)
    errors = validate_documents(files, section)

    if errors:
        return None, errors

    if len(files) == 0:
        return {}, {}

    for field, contents in files.items():
        question = section.get_question(field)

        url = upload_document(
            uploader,
            upload_type,
            documents_url,
            service,
            question.file_settings['name'],
            contents,
            item_number=item_number,
            public=public
        )

        if not url:
            errors[field] = 'file_can_be_saved'
        else:
            files[field] = url

    return files, errors


def upload_declaration_documents(
    uploader,
    upload_type,
    documents_url,
    request_files,
    section,
    framework_slug,
    supplier_id,
    item_number=None,
    public=True
):
    return upload_service_documents(
        uploader,
        upload_type,
        documents_url,
        {
            "frameworkSlug": framework_slug,
            "supplierId": supplier_id
        },
        request_files,
        section,
        item_number=item_number,
        public=public
    )


def upload_fvra_documents(
    uploader,
    upload_type,
    documents_url,
    request_files,
    section,
    framework_slug,
    supplier_id,
    duns_number,
    public=True
):
    return upload_declaration_documents(
        uploader,
        upload_type,
        documents_url,
        request_files,
        section,
        framework_slug,
        supplier_id,
        item_number=duns_number,
        public=public
    )


def file_is_not_empty(file_contents):
    return not file_is_empty(file_contents)


def file_is_empty(file_object):
    return len(get_first_128_bytes(file_object)) == 0


def file_is_less_than_n_mb(file_, number_of_megabytes):
    return get_file_size(file_) < number_of_megabytes * ONE_MEGABYTE_IN_BYTES


def file_is_less_than_5mb(file_):
    return file_is_less_than_n_mb(file_, 5)


def file_is_less_than_10mb(file_):
    return file_is_less_than_n_mb(file_, 10)


def get_first_128_bytes(file_object):
    """Get the contents of a file like object but replace the pointer when we're finished"""
    position = file_object.tell()
    file_object.seek(0)
    contents = file_object.read(128)
    file_object.seek(position)
    return contents


def get_extension(filename):
    file_name, file_extension = os.path.splitext(filename)
    return file_extension.lower()


def get_possible_extensions_from_format(file_object):
    """
    Pass the first 128 bytes from the file object to fleep for a list of possible extensions

    We don't need to load the whole file into memory to let fleep determine the file type. Apparently the first 128
    bytes are sufficient: https://github.com/floyernick/fleep-py/blob/994bc2c274482d80ab13d89d8f7343eb316d3e44/
        fleep/__init__.py#L55

    :param file_object: File object open as bytes.
    :return: list(str): Possible file formats.
    """
    return fleep.get(get_first_128_bytes(file_object)).extension


def extension_matches_possible_file_formats(file_object, extension):
    """
    Pass the first 128 bytes from the file object to fleep and the supplied extension.

    :param file_object: File object open as bytes.
    :param extension: File object open as bytes.
    :return: boolean: Does extension match guess at format?
    """
    return fleep.get(get_first_128_bytes(file_object)).extension_matches(extension.strip('.'))


def generate_file_name(
    framework_slug,
    upload_type,
    supplier_id,
    filename_suffix,
    filename,
    service_id=None,
    item_number=None,
    suffix=None
):
    if suffix is None:
        suffix = default_file_suffix()

    file_name_path = f'{framework_slug}/{upload_type}/{supplier_id}/' + '{file_name}' + f'{get_extension(filename)}'

    if service_id:
        if item_number is None:
            file_name = f'{service_id}-{filename_suffix}-{suffix}'
        else:
            file_name = f'{service_id}-{filename_suffix}-{item_number}-{suffix}'
    elif item_number is not None:
        file_name = f'{filename_suffix}-{item_number}-{suffix}'
    else:
        file_name = f'{filename_suffix}-{suffix}'

    return file_name_path.format(file_name=file_name)


def default_file_suffix():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H%M")


def get_signed_url(bucket, path, base_url):
    url = bucket.get_signed_url(path)
    if url is not None:
        if base_url is not None:
            url = urlparse.urlparse(url)
            base_url = urlparse.urlparse(base_url)
            url = url._replace(netloc=base_url.netloc, scheme=base_url.scheme).geturl()
        return url


# this method is deprecated
def get_agreement_document_path(framework_slug, supplier_id, document_name):
    return '{0}/agreements/{1}/{1}-{2}'.format(
        framework_slug,
        supplier_id,
        document_name
    )


def get_document_path(framework_slug, supplier_id, bucket_category, document_name):
    return '{0}/{1}/{2}/{2}-{3}'.format(
        framework_slug,
        bucket_category,
        supplier_id,
        document_name
    )


def generate_timestamped_document_upload_path(framework_slug, supplier_id, bucket_category, doc_name):
    """Generates a file path with a timestamp inserted before the file extension"""
    file_name, file_extension = os.path.splitext(doc_name)
    timestamped_file_name = file_name + '-' + datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    timestamped_doc_name = timestamped_file_name + file_extension

    return get_document_path(framework_slug, supplier_id, bucket_category, timestamped_doc_name)


def degenerate_document_path_and_return_doc_name(document_path):
    """Takes a document path and returns just the generic document name

    An inverse function for `get_document_path` which returns what would have been
    the `document_name` param (i.e. removes all framework slug, supplier id and bucket category
    information)
    """
    return re.split(r'/\d+-', document_path)[-1]


def sanitise_supplier_name(supplier_name):
    """Replace ampersands with 'and' and spaces with a single underscore."""
    sanitised_supplier_name = supplier_name.encode("ascii", errors="ignore").decode("ascii").strip()
    sanitised_supplier_name = sanitised_supplier_name.replace(' ', '_').replace('&', 'and')
    for bad_char in BAD_SUPPLIER_NAME_CHARACTERS:
        sanitised_supplier_name = sanitised_supplier_name.replace(bad_char, '')
    while '__' in sanitised_supplier_name:
        sanitised_supplier_name = sanitised_supplier_name.replace('__', '_')
    return sanitised_supplier_name


def generate_download_filename(supplier_id, document_name, supplier_name):
    """
        Used for generating supplier-friendly filenames to set as headers in s3 for files,
        such as framework agreement documents, that suppliers need to download
    """
    return '{}-{}-{}'.format(sanitise_supplier_name(supplier_name), supplier_id, document_name)
