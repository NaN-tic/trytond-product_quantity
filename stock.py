# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from dateutil.relativedelta import relativedelta
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction
from trytond.modules.product_quantity.product import QuantityMixin


class Location(QuantityMixin, metaclass=PoolMeta):
    __name__ = 'stock.location'


class Lot(QuantityMixin, metaclass=PoolMeta):
    __name__ = 'stock.lot'
