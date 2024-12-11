# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from dateutil.relativedelta import relativedelta
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction


class QuantityMixin:
    __slots__ = ()
    available_quantity = fields.Function(fields.Float('Available Quantity'),
        'get_quantity', searcher='search_quantity')
    incoming_quantity = fields.Function(fields.Float('Incoming Quantity'),
        'get_quantity', searcher='search_quantity')
    outgoing_quantity = fields.Function(fields.Float('Outgoing Quantity'),
        'get_quantity', searcher='search_quantity')

    @classmethod
    def _quantity_context(cls, name):
        pool = Pool()
        Date = pool.get('ir.date')
        Configuration = pool.get('stock.configuration')

        config = Configuration(1)
        lag_days = config.lag_days or 0
        today = Date.today() + relativedelta(days=int(lag_days))

        new_context = {}
        if name == 'available_quantity':
            new_context['stock_assign'] = True
            new_context['stock_date_end'] = today
            new_context['with_childs'] = True
        elif name == 'incoming_quantity':
            # new_context['forecast'] = False
            new_context['stock_date_end'] = today
            # new_context['forecast_date'] = today
            new_context['with_childs'] = False
        elif name == 'outgoing_quantity':
            new_context['forecast'] = True
            new_context['stock_date_end'] = today
            new_context['forecast_date'] = today
            new_context['with_childs'] = False
        else:
            new_context = super()._quantity_context(name)
        return new_context

    @classmethod
    def _quantity_locations(cls, name):
        pool = Pool()
        Configuration = pool.get('stock.configuration')
        Location = pool.get('stock.location')

        context = Transaction().context

        location_ids = []
        if not context.get('locations'):
            config = Configuration(1)
            warehouse_id = context.get('warehouse')

            warehouses = []
            if config.warehouse_quantity == 'all':
                warehouses = Location.search([('type', '=', 'warehouse')])
            elif warehouse_id and config.warehouse_quantity == 'user':
                warehouses = [Location(warehouse_id)]

            if name == 'incoming_quantity':
                location_ids = [w.input_location.id for w in warehouses
                    if w.input_location]
            elif name == 'outgoing_quantity':
                location_ids = [w.output_location.id for w in warehouses
                    if w.output_location]
            else:
                location_ids = [w.storage_location.id for w in warehouses
                    if w.storage_location]
        return location_ids

    @classmethod
    def get_quantity(cls, products, name):
        with Transaction().set_context(locations=cls._quantity_locations(name)):
            return super().get_quantity(products, name)

    @classmethod
    def search_quantity(cls, name, domain=None):
        with Transaction().set_context(locations=cls._quantity_locations(name)):
            return super().search_quantity(name, domain)


class Template(metaclass=PoolMeta):
    __name__ = 'product.template'
    available_quantity = fields.Function(fields.Float('Available Quantity'),
        'get_product_quantity')
    incoming_quantity = fields.Function(fields.Float('Incoming Quantity'),
        'get_product_quantity')
    outgoing_quantity = fields.Function(fields.Float('Outgoing Quantity'),
        'get_product_quantity')

    def get_product_quantity(self, name):
        return sum([getattr(p, name) or 0 for p in self.products
            if hasattr(p, name)])


class Product(QuantityMixin, metaclass=PoolMeta):
    __name__ = 'product.product'
