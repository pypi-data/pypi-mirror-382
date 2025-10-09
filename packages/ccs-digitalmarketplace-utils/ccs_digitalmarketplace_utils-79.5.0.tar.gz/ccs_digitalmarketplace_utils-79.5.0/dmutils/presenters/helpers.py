from jinja2.filters import escape


def empty_table(text):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if len(args[0]) == 0:
                return {"rows": [[{"text": text}]]}

            return func(*args, **kwargs)

        return wrapper

    return decorator


def link_html(href, text, visually_hidden_text=None):
    visually_hidden_html = (
        f'<span class="govuk-visually-hidden">{escape(visually_hidden_text)}</span>'
        if visually_hidden_text
        else ""
    )

    return f'<a class="govuk-link" href="{href}">{escape(text)}{visually_hidden_html}</a>'
