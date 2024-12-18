# This file is part product_quantity module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase


class ProductQuantityTestCase(ModuleTestCase):
    'Test Product Quantity module'
    module = 'product_quantity'
    extras = ['stock_lot']

del ModuleTestCase
