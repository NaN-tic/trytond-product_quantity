# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import operator
from dateutil.relativedelta import relativedelta
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.transaction import Transaction
from sql.aggregate import Sum
from sql.conditionals import Coalesce


class QuantityMixin:
    __slots__ = ()
    available_quantity = fields.Function(fields.Float('Available Quantity'),
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
        else:
            new_context = super()._quantity_context(name)
        return new_context

    @classmethod
    def _quantity_locations(cls, name=None):
        pool = Pool()
        Configuration = pool.get('stock.configuration')
        Location = pool.get('stock.location')

        context = Transaction().context

        location_ids = context.get('locations', [])
        if not context.get('locations'):
            config = Configuration(1)
            warehouse_id = context.get('warehouse')

            warehouses = []
            if warehouse_id and config.warehouse_quantity == 'user':
                warehouses = [Location(warehouse_id)]
            elif (config.warehouse_quantity == 'all'
                    or config.warehouse_quantity is None):
                warehouses = Location.search([('type', '=', 'warehouse')])

            if warehouses:
                location_ids = [w.id for w in warehouses]
        return location_ids

    @classmethod
    def get_quantity(cls, products, name):
        context = Transaction().context

        if not context.get('locations'):
            with Transaction().set_context(locations=cls._quantity_locations(name),
                    with_childs=True):
                return super().get_quantity(products, name)
        return super().get_quantity(products, name)

    @classmethod
    def search_quantity(cls, name, domain=None):
        context = Transaction().context

        if not context.get('locations'):
            with Transaction().set_context(locations=cls._quantity_locations(name),
                    with_childs=True):
                return super().search_quantity(name, domain)
        return super().search_quantity(name, domain)


class QuantityByMixin:
    __slots__ = ()
    incoming_quantity = fields.Function(fields.Float('Incoming Quantity'),
        'get_in_out_quantity',searcher='search_in_out_quantity')
    outgoing_quantity = fields.Function(fields.Float('Outgoing Quantity'),
        'get_in_out_quantity', searcher='search_in_out_quantity')

    @classmethod
    def get_in_out_quantity(cls, products, name):
        product_ids = list(map(int, products))
        res = dict((x, 0) for x in product_ids)
        if not products:
            return res

        direction = 'in' if name == 'incoming_quantity' else 'out'
        pbl = cls._get_in_out_quantity(product_ids, direction)
        for product_id in product_ids:
            res[product_id] = pbl.get(product_id, 0)
        return res

    @classmethod
    def _get_in_out_quantity(cls, product_ids=[], direction='in'):
        pool = Pool()
        Location = pool.get('stock.location')
        Move = pool.get('stock.move')

        move = Move.__table__()

        transaction = Transaction()
        context = transaction.context
        cursor = transaction.connection.cursor()

        location_ids = context.get('locations')
        if not location_ids:
            location_ids = cls._quantity_locations()
        if not location_ids:
            return {}

        locations = Location.search([
                ('parent', 'child_of', location_ids),
                ('type', '=', 'storage'),
                ])
        location_ids = list(set(x.id for x in locations))
        if not location_ids:
            return {}

        sql_where = move.company == context.get('company', -1)
        sql_where &= move.state == 'draft'
        if product_ids:
            sql_where &= move.product.in_(product_ids)
        if direction == 'in':
            location_supplier_ids = [l.id for l in Location.search([
                ('type', '=', 'supplier'),
                ])]
            if not location_supplier_ids:
                return {}
            sql_where &= move.from_location.in_(location_supplier_ids)
            sql_where &= move.to_location.in_(location_ids)
        else:
            location_customer_ids = [l.id for l in Location.search([
                ('type', '=', 'customer'),
                ])]
            if not location_customer_ids:
                return {}
            sql_where &= move.from_location.in_(location_ids)
            sql_where &= move.to_location.in_(location_customer_ids)

        query = move.select(
            move.product,
            Coalesce(Sum(move.internal_quantity), 0).as_('quantity'),
            where=sql_where,
            group_by=move.product)
        cursor.execute(*query)

        return {product_id: quantity for product_id, quantity in cursor.fetchall()}

    @classmethod
    def search_in_out_quantity(cls, name, domain=None):
        _, operator_, operand = domain

        direction = 'in' if name == 'incoming_quantity' else 'out'
        pbl = cls._get_in_out_quantity(product_ids=[], direction=direction)

        operator_ = {
            '=': operator.eq,
            '>=': operator.ge,
            '>': operator.gt,
            '<=': operator.le,
            '<': operator.lt,
            '!=': operator.ne,
            'in': lambda v, l: v in l,
            'not in': lambda v, l: v not in l,
            }.get(operator_, lambda v, l: False)
        record_ids = []
        for product, quantity in pbl.items():
            if (quantity is not None and operand is not None
                    and operator_(quantity, operand)):
                record_ids.append(product)

        return [('id', 'in', record_ids)]


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


class Product(QuantityMixin, QuantityByMixin, metaclass=PoolMeta):
    __name__ = 'product.product'
