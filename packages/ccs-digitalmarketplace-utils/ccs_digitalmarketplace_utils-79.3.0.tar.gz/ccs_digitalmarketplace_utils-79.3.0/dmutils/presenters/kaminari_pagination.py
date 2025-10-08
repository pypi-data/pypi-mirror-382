import math


# The pagination logic is copied from the Kaminari ruby gem (https://github.com/kaminari/kaminari)
# which I use on other projects and know it works well
class KaminariPagination:
    def __init__(self, total_items, per_page, current_page, **kwargs):
        self.current_page = int(current_page)
        self.total_pages = math.ceil(total_items / per_page)
        self.outer_window = kwargs.get('outer_window', 0)
        self.window = kwargs.get('window', 4)

    def pagination_parts(self):
        options = {
            'current_page': self.current_page,
            'total_pages': self.total_pages,
            'outer_window': self.outer_window,
            'window': self.window,
        }
        last = None

        pagination_parts = {
            'items': []
        }

        if self.current_page != 1:
            pagination_parts['previous'] = {
                'page': self.current_page - 1
            }

        for page in self._relevant_pages():
            page_link = self._PaginationPageProxy(
                options,
                page,
                last
            )

            if page_link.should_display_link:
                pagination_parts['items'].append({
                    'page': page_link.page,
                    'current': page_link.is_current
                })
            elif not page_link.was_truncated:
                pagination_parts['items'].append({
                    'ellipsis': True
                })
                page_link.pagination_item_type = 'gap'

            last = page_link

        if self.current_page < self.total_pages:
            pagination_parts['next'] = {
                'page': self.current_page + 1
            }

        return pagination_parts

    def _relevant_pages(self):
        left_window_plus_one = list(
            range(1, self.outer_window + 2)
        )
        right_window_plus_one = list(
            range(self.total_pages - self.outer_window, self.total_pages + 1)
        )
        inside_window_plus_each_sides = list(
            range(self.current_page - self.window - 1, self.current_page + self.window + 2)
        )

        return sorted([
            page
            for page in set(left_window_plus_one + inside_window_plus_each_sides + right_window_plus_one)
            if page >= 1 and page <= self.total_pages
        ])

    class _PaginationPageProxy:
        pagination_item_type = 'number'

        def __init__(
            self,
            options: dict,
            page: int,
            last
        ) -> None:
            self.page = page
            self.current_page = options['current_page']
            self.total_pages = options['total_pages']
            self.outer_window = options['outer_window']
            self.window = options['window']
            self.was_truncated = last and last.pagination_item_type == 'gap'

        @property
        def is_current(self):
            return self.page == self.current_page

        @property
        def is_left_outer(self):
            return self.page <= self.outer_window

        @property
        def is_right_outer(self):
            return self.total_pages - self.page < self.outer_window

        @property
        def is_inside_window(self):
            return abs(self.current_page - self.page) <= self.window

        @property
        def is_single_gap(self):
            return (
                (
                    (self.page == self.current_page - self.window - 1)
                    and (self.page == self.outer_window + 1)
                )
                or (
                    (self.page == self.current_page + self.window + 1)
                    and (self.page == self.total_pages - self.outer_window)
                )
            )

        @property
        def should_display_link(self):
            return self.is_left_outer or self.is_right_outer or self.is_inside_window or self.is_single_gap
