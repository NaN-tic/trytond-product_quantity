# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import configuration
from . import product
from . import stock

def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationProductQuantity,
        product.Template,
        product.Product,
        stock.Location,
        stock.ProductsByLocations,
        module='product_quantity', type_='model')
    Pool.register(
        stock.Lot,
        stock.LotsByLocations,
        depends=['stock_lot'],
        module='product_quantity', type_='model')
