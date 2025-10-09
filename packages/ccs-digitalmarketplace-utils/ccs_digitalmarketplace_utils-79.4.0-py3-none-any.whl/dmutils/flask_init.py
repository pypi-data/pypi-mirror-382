from collections import OrderedDict
import os
from types import MappingProxyType

from dmutils import config, logging, proxy_fix, request_id, formats, filters, cookie_probe
from dmutils.errors import api as api_errors, frontend as fe_errors
from dmutils.urls import SafePurePathConverter
import dmutils.session
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import default_exceptions


frontend_error_handlers = MappingProxyType(OrderedDict((
    (CSRFError, fe_errors.csrf_handler,),
    (400, fe_errors.render_error_page,),
    (401, fe_errors.redirect_to_login,),
    (403, fe_errors.redirect_to_login,),
    (404, fe_errors.render_error_page,),
    (410, fe_errors.render_error_page,),
    (503, fe_errors.render_error_page,),
    (500, fe_errors.render_error_page,),
)))


api_error_handlers = MappingProxyType(OrderedDict(
    (
        (api_errors.ValidationError, api_errors.validation_error_handler,),
    ) + tuple(
        (code, api_errors.json_error_handler) for code in default_exceptions
    ),
))


def init_app(
    application,
    config_object,
    bootstrap=None,
    data_api_client=None,
    search_api_client=None,
    tasks_api_client=None,
    cdp_api_client=None,
    insights_api_client=None,
    db=None,
    login_manager=None,
    error_handlers=frontend_error_handlers,
):

    application.config.from_object(config_object)
    if hasattr(config_object, 'init_app'):
        config_object.init_app(application)

    application.config.from_object(__name__)

    # all belong to dmutils
    config.init_app(application)
    logging.init_app(application)
    proxy_fix.init_app(application)
    request_id.init_app(application)
    cookie_probe.init_app(application)

    for initable_object in [
        bootstrap,
        cdp_api_client,
        data_api_client,
        db,
        login_manager,
        search_api_client,
        tasks_api_client,
        insights_api_client,
    ]:
        if initable_object:
            initable_object.init_app(application)

    if login_manager:
        dmutils.session.init_app(application)

    # allow us to use <safepurepath:...> components in route patterns
    application.url_map.converters["safepurepath"] = SafePurePathConverter

    # Set the govuk rebrand to false
    application.jinja_env.globals["govukRebrand"] = True

    @application.after_request
    def add_header(response):
        # Block sites from rendering our views inside <iframe>, <embed>, etc by default.
        # Individual views may set their own value (e.g. 'SAMEORIGIN')
        if not response.headers.get('X-Frame-Options'):
            response.headers.setdefault('X-Frame-Options', 'DENY')
        return response

    for template_filter in [
        # Make filters accessible in templates.
        filters.capitalize_first,
        filters.format_links,
        filters.nbsp,
        filters.smartjoin,
        filters.preserve_line_breaks,
        filters.sub_country_codes,
        filters.parse_document_upload_time,
        # Make select formats available in templates.
        formats.dateformat,
        formats.datetimeformat,
        formats.datetodatetimeformat,
        formats.displaytimeformat,
        formats.shortdateformat,
        formats.timeformat,
        formats.utcdatetimeformat,
        formats.utctoshorttimelongdateformat,
    ]:
        application.add_template_filter(template_filter)

    @application.context_processor
    def inject_global_template_variables():
        return dict(
            pluralize=pluralize,
            **(application.config['BASE_TEMPLATE_DATA'] or {}))

    for exc_or_code, handler in error_handlers.items():
        application.register_error_handler(exc_or_code, handler)


def pluralize(count, singular, plural):
    return singular if count == 1 else plural


def get_extra_files(paths):
    for path in paths:
        for dirname, dirs, files in os.walk(path):
            for filename in files:
                filename = os.path.join(dirname, filename)
                if os.path.isfile(filename):
                    yield filename
