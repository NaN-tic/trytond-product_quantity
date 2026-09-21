import unittest

from proteus import Model
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):
        activate_modules(['product_quantity', 'purchase_request', 'stock_lot'])

        Uom = Model.get('product.uom')
        Template = Model.get('product.template')
        PurchaseRequest = Model.get('purchase.request')
        unit, = Uom.find([('name', '=', 'Unit')])
        template = Template(name='Product', default_uom=unit)
        template.save()
        product, = template.products
        line = PurchaseRequest()
        line.product = product

        for name in ('forecast_quantity', 'available_quantity',
                'incoming_quantity', 'outgoing_quantity'):
            self.assertEqual(getattr(line, name), getattr(product, name))
