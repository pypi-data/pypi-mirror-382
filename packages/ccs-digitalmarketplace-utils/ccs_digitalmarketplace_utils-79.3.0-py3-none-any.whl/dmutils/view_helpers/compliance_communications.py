from flask import session, abort, flash, redirect

from ..presenters.pagination import generate_govuk_frontend_pagination_params

from .frameworks import get_framework_or_404
from .pagination import default_pagination_config


NO_CATEGORY_ERROR_MESSAGE = "You must have a category"
NO_SUBJECT_ERROR_MESSAGE = "You must have a subject"
NO_MESSAGE_ERROR_MESSAGE = "You must have a message"


def get_framework_and_check_communications_allowed_or_404(client, framework_slug):
    framework = get_framework_or_404(
        client,
        framework_slug,
        [
            'open',
            'pending',
            'standstill',
            'live',
            'expired'
        ]
    )

    if not framework['hasCommunications']:
        abort(404)

    return framework


def get_compliance_communications_content(
    request,
    table_params_method,
    data,
    page_param,
    preserved_kwargs,
    url_params,
    with_supplier=False
):
    return {
        "table_params": table_params_method(
            data['communications'],
            with_supplier
        ),
        "pagination_params": generate_govuk_frontend_pagination_params(
            default_pagination_config(data['meta'], request, page_param),
            url_params,
            {
                "request_args": request.args,
                "preserved_kwargs": preserved_kwargs,
                "page_param": page_param
            }
        )
    }


def get_new_supplier_message_and_category_or_redirect(supplier_id, framework_slug, redirect_url):
    new_supplier_message = session.get(f"{supplier_id}-{framework_slug}")

    if new_supplier_message is None:
        no_category = True
    else:
        category = new_supplier_message.get('category')
        no_category = category is None

    if no_category:
        flash(NO_CATEGORY_ERROR_MESSAGE, 'error')
        return (
            None,
            None,
            redirect(redirect_url)
        )

    return new_supplier_message, category, None


def get_subject_or_redirect(new_supplier_message, redirect_url):
    subject = new_supplier_message.get('subject')

    if subject is None:
        flash(NO_SUBJECT_ERROR_MESSAGE, 'error')
        return (
            None,
            redirect(redirect_url)
        )

    return subject, None


def get_message_and_attachments_or_redirect(new_supplier_message, redirect_url):
    message = new_supplier_message.get('message')
    attachments = new_supplier_message.get('attachments')

    if message is None:
        flash(NO_MESSAGE_ERROR_MESSAGE, 'error')
        return (
            None,
            None,
            redirect(redirect_url)
        )

    return message, attachments, None
