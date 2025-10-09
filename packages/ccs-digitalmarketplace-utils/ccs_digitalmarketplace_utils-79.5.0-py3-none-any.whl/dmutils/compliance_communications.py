import os

from .documents import file_is_not_empty
from .forms.compliance_communications import MAX_NUMBER_OF_ATTACHMENTS
from .s3 import S3ResponseError


def upload_communication_attachments(
    uploader,
    framework_slug,
    supplier_id,
    message_id,
    request_files,
    temporary=False
):
    attachment_fields = [
        f"attachments-{index}-file"
        for index in range(MAX_NUMBER_OF_ATTACHMENTS)
    ]
    files = {field: file for field, file in request_files.items() if field in attachment_fields}
    files = filter_empty_files(files)
    errors = {}

    if len(files) == 0:
        return {}, {}

    for field, file in files.items():
        url = upload_communication(
            uploader,
            framework_slug,
            supplier_id,
            message_id,
            file,
            temporary=temporary
        )

        if not url:
            errors[field] = 'file_cannot_be_saved'
        else:
            files[field] = url

    return files, errors


def upload_communication(
    uploader,
    framework_slug,
    supplier_id,
    message_id,
    file,
    temporary=False
):
    file_path, file_name = generate_file_name(
        framework_slug,
        supplier_id,
        message_id,
        file.filename,
        temporary=temporary
    )

    try:
        uploader.save(
            f'{file_path}/{file_name}',
            file,
            acl='bucket-owner-full-control'
        )
    except S3ResponseError:
        return False

    return file_name


def get_compliance_communication_path_root(framework_slug, supplier_id, message_id, temporary=False):
    if temporary:
        path_template = '{}/communications/compliance-communications/temp/{}/{}'
    else:
        path_template = '{}/communications/compliance-communications/{}/{}'

    return path_template.format(
        framework_slug,
        supplier_id,
        message_id,
    )


def generate_file_name(
    framework_slug,
    supplier_id,
    message_id,
    filename,
    temporary=False
):
    file_name, file_extension = os.path.splitext(filename)

    filepath = f'{file_name.replace(" ", "_")}{file_extension.lower()}'

    return (
        get_compliance_communication_path_root(
            framework_slug,
            supplier_id,
            message_id,
            temporary=temporary
        ),
        filepath
    )


def move_attachment_from_temp_folder(
    mover,
    communications_bucket,
    framework_slug,
    supplier_id,
    old_message_id,
    new_message_id,
    object_key
):
    src_root = get_compliance_communication_path_root(
        framework_slug,
        supplier_id,
        old_message_id,
        temporary=True
    )
    src_key = f'{src_root}/{object_key}'

    if mover.copy(
        src_bucket=communications_bucket,
        src_key=src_key,
        target_key=src_key.replace('/temp', '').replace(str(old_message_id), str(new_message_id))
    ):
        mover.delete_key(src_key)


def filter_empty_files(files):
    return {
        key: file for key, file in files.items()
        if file_is_not_empty(file)
    }
