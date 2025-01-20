# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields
from trytond.modules.product_quantity.product import QuantityMixin, QuantityByMixin


class Location(QuantityMixin, metaclass=PoolMeta):
    __name__ = 'stock.location'


class Lot(QuantityMixin, QuantityByMixin, metaclass=PoolMeta):
    __name__ = 'stock.lot'


class ProductsByLocations(metaclass=PoolMeta):
    __name__ = 'stock.products_by_locations'
    available_quantity = fields.Function(fields.Float('Available Quantity'),
        'get_product', searcher='search_product')
    incoming_quantity = fields.Function(fields.Float('Incoming Quantity'),
        'get_product', searcher='search_product')
    outgoing_quantity = fields.Function(fields.Float('Outgoing Quantity'),
        'get_product', searcher='search_product')


class LotsByLocations(metaclass=PoolMeta):
    __name__ = 'stock.lots_by_locations'
    available_quantity = fields.Function(fields.Float('Available Quantity'),
        'get_lot', searcher='search_lot')
    incoming_quantity = fields.Function(fields.Float('Incoming Quantity'),
        'get_lot', searcher='search_lot')
    outgoing_quantity = fields.Function(fields.Float('Outgoing Quantity'),
        'get_lot', searcher='search_lot')
