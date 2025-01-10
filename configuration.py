# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.modules.company.model import CompanyValueMixin


warehouse_quantity = fields.Selection([
        ('all', 'All Warehouses'),
        ('user', 'User Warehouse'),
    ], 'Warehouse Quantity', help="Warehouse to use in Quantity fields in the product.")
lag_days = fields.Numeric('Number of lag days', digits=(16, 0), help="Number of days "
    "to be added to the current day to compute Forecast, Incoming and Outgoing Quantity "
    "fields in product. Leave empty to take into account all future moves.")


class Configuration(metaclass=PoolMeta):
    __name__ = 'stock.configuration'
    warehouse_quantity = fields.MultiValue(warehouse_quantity)
    lag_days = fields.MultiValue(lag_days)

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in ('warehouse_quantity', 'lag_days'):
            return pool.get('stock.configuration.product_quantity')
        return super(Configuration, cls).multivalue_model(field)


class ConfigurationProductQuantity(ModelSQL, CompanyValueMixin):
    "Stock Configuration - Product Quantity"
    __name__ = 'stock.configuration.product_quantity'
    warehouse_quantity = warehouse_quantity
    lag_days = lag_days
