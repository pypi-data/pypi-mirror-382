from flask import url_for

from .kaminari_pagination import KaminariPagination

from ..view_helpers.pagination import get_pagination_args


def generate_govuk_frontend_pagination_params(pagination_config, url_params, url_arg_params):
    pagination_parts = KaminariPagination(**pagination_config).pagination_parts()

    if pagination_parts.get('previous'):
        url_arg_params["page"] = pagination_parts["previous"]["page"]

        pagination_parts['previous']['href'] = url_for(
            url_params['endpoint'],
            **url_params.get('params', {}),
            **get_pagination_args(**url_arg_params)
        )
        pagination_parts["previous"].pop("page")

    for pagination_part_item in pagination_parts['items']:
        if not pagination_part_item.get('ellipsis'):
            url_arg_params["page"] = pagination_part_item["page"]

            pagination_part_item['href'] = url_for(
                url_params['endpoint'],
                **url_params.get('params', {}),
                **get_pagination_args(**url_arg_params)
            )
            pagination_part_item["number"] = pagination_part_item.pop("page")

    if pagination_parts.get('next'):
        url_arg_params["page"] = pagination_parts["next"]["page"]

        pagination_parts['next']['href'] = url_for(
            url_params['endpoint'],
            **url_params.get('params', {}),
            **get_pagination_args(**url_arg_params)
        )
        pagination_parts["next"].pop("page")

    return pagination_parts
