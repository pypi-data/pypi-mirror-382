import re

from .fields import (
    DMRadioField,
    DMStripWhitespaceStringField,
    DMFileField,
)
from .widgets import DMTextArea
from ..s3 import get_file_size
from ..documents import (
    ONE_MEGABYTE_IN_BYTES,
    FILE_TYPE_TO_VALIDATION
)

from flask_wtf import FlaskForm
from wtforms.fields import FieldList, FormField
from wtforms.validators import (
    InputRequired,
    Length,
    ValidationError
)


MAX_NUMBER_OF_ATTACHMENTS = 20


def word_length(limit, message):
    message = message % limit

    def _length(form, field):
        if not field.data or not limit:
            return field

        if len(field.data.split()) > limit:
            raise ValidationError(message)

    return _length


class ComplianceCommunicationCategoryForm(FlaskForm):
    def __init__(self, framework_categories, **kwargs):
        super().__init__(**kwargs)
        self.framework_categories = framework_categories

        self.category.options = [
            {
                "value": category,
                "label": category.capitalize()
            }
            for category in framework_categories
        ]

    category = DMRadioField(
        "Select the appropriate category for your message thread",
        validators=[
            InputRequired(message='You must select an option')
        ]
    )


class ComplianceCommunicationSubjectForm(FlaskForm):
    def __init__(self, data_api_client, framework_slug, supplier_id, **kwargs):
        super().__init__(**kwargs)
        self.data_api_client = data_api_client
        self.framework_slug = framework_slug
        self.supplier_id = supplier_id

    subject = DMStripWhitespaceStringField(
        "Enter the subject for the message thread",
        validators=[
            InputRequired(message="You must enter the subject for the message thread"),
            Length(max=100, message="The subject must be no more than 100 characters"),
        ]
    )

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        valid = True

        if self.subject.data.lower() in [
            communication['subject'].lower() for communication in self.data_api_client.find_communications_iter(
                framework=self.framework_slug,
                supplier_id=self.supplier_id
            )
        ]:
            self.subject.errors.append(
                "This subject has already been used for another message thread. The subject must be unique"
            )
            valid = False

        return valid


class ComplianceCommunicationMessageAttachmentForm(FlaskForm):
    file = DMFileField(
        "File",
        hint='The filename can only contain letters, numbers, spaces and/or underscores',
        validators=[]
    )
    required = DMStripWhitespaceStringField(
        "Attachment required",
        hint="Check this to include this attachment",
        validators=[],
    )

    def validate_attachment(self, index, required_attachment_filenames):
        if not self.validate():
            return False

        allowed_characters_pattern = re.compile(r'^[a-zA-Z0-9 _]*\.[a-zA-Z]+$')

        if not self.file.data or not self.file.data.filename:
            self.file.errors.append(
                f"You must select a file for attachment {index}"
            )

            return False

        if len(self.file.data.filename) > 100:
            self.file.errors.append(
                f"The filename for attachment {index} must be no more than 100 characters"
            )

            return False

        if not allowed_characters_pattern.match(self.file.data.filename):
            self.file.errors.append(
                f"The filename for attachment {index} can only contain letters, numbers, spaces and/or underscores"
            )

            return False

        if self.file.data.filename.lower() in [
            attachment_name.lower()
            for i, attachment_name in enumerate(required_attachment_filenames, 1)
            if index != i
        ]:
            self.file.errors.append(
                "You already have an attachment with this filename. The attachment filename must be unique"
            )

            return False

        if not any(
            file_is_format(self.file.data)
            for file_is_format in
            FILE_TYPE_TO_VALIDATION.values()
        ):
            self.file.errors.append(
                f"The file type for attachment {index} is not valid"
            )

            return False

        return True


class ComplianceCommunicationMessageForm(FlaskForm):
    def __init__(self, max_total_file_size_in_mb, **kwargs):
        super().__init__(**kwargs)
        self.max_total_file_size_in_mb = max_total_file_size_in_mb

    message = DMStripWhitespaceStringField(
        "Enter the message",
        widget=DMTextArea(max_length_in_words=500),
        validators=[
            InputRequired(message="You must enter a message"),
            Length(max=5000, message="The message must be no more than 5000 characters"),
            word_length(500, "The message must be no more than %d words"),
        ]
    )

    attachments = FieldList(
        FormField(ComplianceCommunicationMessageAttachmentForm),
        min_entries=MAX_NUMBER_OF_ATTACHMENTS,
        max_entries=MAX_NUMBER_OF_ATTACHMENTS
    )

    def required_attachment_names(self):
        return [
            (
                attachment.file.data.filename.lower()
            )
            for attachment in self.attachments
            if attachment.required.data and attachment.file.data
        ]

    def validate(self, extra_validators=None):
        # We have to the validation manually as we only validate the required attachments
        valid = True

        if not super().validate(extra_validators):
            valid = False

        required_attachment_names = self.required_attachment_names()

        for index, attachment in enumerate(self.attachments, 1):
            if attachment.required.data:
                if not attachment.validate_attachment(index, required_attachment_names):
                    valid = False
            else:
                attachment.file.raw_data = None
                attachment.file.data = None

        if valid:
            if sum(
                get_file_size(attachment.file.data)
                for attachment in self.attachments
                if attachment.required.data
            ) > (self.max_total_file_size_in_mb * ONE_MEGABYTE_IN_BYTES):
                for attachment in self.attachments:
                    if attachment.required.data:
                        attachment.file.errors.append(
                            f"The total size for all attachments cannot exceed {self.max_total_file_size_in_mb}MB"
                        )

                valid = False

        return valid

    def add_attachment_upload_errors(self, upload_errors):
        for index, attachment in enumerate(self.attachments, 1):
            if attachment.file.name in upload_errors:
                attachment.file.errors.append(f"Attachment {index} failed to upload. Please try again.")
