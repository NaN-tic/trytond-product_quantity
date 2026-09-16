from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction


class ProductQuantitySaleLineTestCase(ModuleTestCase):
    module = 'product_quantity'
    extras = ['sale', 'stock_lot']

    @with_transaction()
    def test(self):
        pool = Pool()
        Uom = pool.get('product.uom')
        Template = pool.get('product.template')
        Product = pool.get('product.product')
        unit, = Uom.search([('name', '=', 'Unit')])
        template, = Template.create([{
            'name': 'Product', 'default_uom': unit.id}])
        product, = Product.create([{'template': template.id}])
        line = pool.get('sale.line')(product=product)
        for name in ('forecast_quantity', 'available_quantity',
                'incoming_quantity', 'outgoing_quantity'):
            self.assertEqual(line.get_product_quantity(name),
                getattr(product, name))


del ModuleTestCase
