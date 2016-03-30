import math

class Paginater():

    """
    Adapted from http://web2py.com/books/default/chapter/29/14/other-recipes#Pagination
    """

    item_limits = [12, 25, 50, 100, 200]

    def __init__(self, request, query_set):
        self._request = request
        self._query_set = query_set

        self.page = None
        self.items_per_page = None
        self.limitby = None
        self.item_count = None
        self.pages = None
        self.has_next = None
        self.has_prev = None
        self.next_page = None
        self.prev_page = None

        self.set_vars(query_set)

    def set_vars(self, query_set):

        self.page = (int(self._request.vars["page"] or 0))
        self.items_per_page = (int(self._request.vars["per"] or Paginater.item_limits[0]))
        if not self.items_per_page in Paginater.item_limits:
            self.items_per_page = Paginater.item_limits[0]
        self.limitby=(self.page*self.items_per_page,(self.page+1)*self.items_per_page)  # 1*5 <-> 2*5+1

        self.item_count = query_set.count()
        division = self.item_count / float(self.items_per_page)
        self.pages = int(math.floor(division))  # don't need a new page for not full pages ie. 11/12
        if division % 1 == 0:
            self.pages -= 1  # don't need a new page for a full page ie. 12/12 items
        self.has_next = self.page < self.pages  # need a new page for overfull page ie. 13/12 items, need page for 1/12
        self.has_prev = bool(self.page)
        self.next_page = None if not self.has_next else self.page+1  # href='{{=URL(vars=dict(page=paginater.next_page))}}'
        self.prev_page = None if not self.has_prev else self.page-1
