# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of the repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from .product import ProductQuantityLineMixin


class PurchaseLine(ProductQuantityLineMixin, metaclass=PoolMeta):
    __name__ = 'purchase.line'


class PurchaseRequest(ProductQuantityLineMixin, metaclass=PoolMeta):
    __name__ = 'purchase.request'
