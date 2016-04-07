import math
from gluon import URL, SPAN

class Paginater():

    """
    Adapted from http://web2py.com/books/default/chapter/29/14/other-recipes#Pagination
    """

    item_limits = map(lambda x: x/4, [12, 25, 50, 100, 200])

    def __init__(self, request, query_set, db):
        self._request = request
        self._query_set = query_set
        self._db = db

        self.page = None
        self.items_per_page = None
        self.limitby = None

        self.orderby = None
        self.order_table = None
        self.order_field = None
        self.order_links = {}
        self.order_reverse = False

        self.item_count = None
        self.pages = None
        self.has_next = None
        self.has_prev = None
        self.next_page = None
        self.prev_page = None

        self.set_ordering()
        self.set_paging()

    def set_ordering(self):
        order_string = self._request.vars["orderby"] or (self._request.function + ".id")
        self.order_reverse = "~" in order_string
        order_string = order_string.strip("~")
        self.order_table, self.order_field = order_string.split(".")
        if self.order_reverse:
            self.orderby = ~self._db[self.order_table][self.order_field]
        else:
            self.orderby = self._db[self.order_table][self.order_field]

        if 'first_name' == self.order_field:
            self.orderby = self.orderby|self._db[self.order_table]["last_name"]
        elif "last_name" == self.order_field:  # if 2 people have the same last name, then sort by first name
            self.orderby = self.orderby|self._db[self.order_table]["first_name"]

        for table_name in self._db.tables:
            for table_field in self._db[table_name].fields:
                table_field_is_order_field = (table_name == self.order_table) & (self.order_field == table_field)
                self.order_links.setdefault(table_name, {}).setdefault(table_field, {}).update({  # http://stackoverflow.com/questions/12905999/python-dict-how-to-create-key-or-append-an-element-to-key
                    "url": URL(vars=dict(self._request.vars.items() + {'orderby': ("" if (not table_field_is_order_field or self.order_reverse) else "~") + "%s.%s"%(table_name, table_field)}.items())),  # flipping order
                    "arrow": SPAN(_class="text-info glyphicon glyphicon-arrow-" + ("down" if self.order_reverse else "up")) if table_field_is_order_field else ""
                })

    def set_paging(self):
        self.page = (int(self._request.vars["page"] or 0))
        self.items_per_page = (int(self._request.vars["per"] or Paginater.item_limits[0]))
        if not self.items_per_page in Paginater.item_limits:
            self.items_per_page = Paginater.item_limits[0]
        self.limitby=(self.page*self.items_per_page,(self.page+1)*self.items_per_page)  # 1*5 <-> 2*5+1

        self.item_count = self._query_set.count()
        division = self.item_count / float(self.items_per_page)
        self.pages = int(math.floor(division))  # don't need a new page for not full pages ie. 11/12
        if division % 1 == 0:  # fixme - there may be a bug with left inner join as not all left from (db.table>0) will show up if right is missing, use left outer join instead.
            self.pages -= 1  # don't need a new page for a full page ie. 12/12 items
        self.has_next = self.page < self.pages  # need a new page for overfull page ie. 13/12 items, need page for 1/12
        self.has_prev = bool(self.page)
        self.next_page = None if not self.has_next else self.page+1  # href='{{=URL(vars=dict(page=paginater.next_page))}}'
        self.prev_page = None if not self.has_prev else self.page-1
