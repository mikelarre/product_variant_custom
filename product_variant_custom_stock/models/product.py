# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductVersion(models.Model):
    _inherit = "product.version"

    initial_stock = fields.Float(string="Initial Stock")
    initial_stock_date = fields.Datetime(string="Initial Stock Date")
    real_stock = fields.Float(string="Real Stock",
                              compute="_compute_version_stock", store="True")
    virtual_stock = fields.Float(string="Virtual Stock",
                                 compute="_compute_version_stock",
                                 store="True")

    @api.depends("initial_stock", "initial_stock_date")
    def _compute_version_stock(self):
        move_obj = self.env['stock.move']
        for product in self:
            initial_date = product.initial_stock_date
            domain = [('product_version_id', '=', product.id),
                      ('date', '>=', initial_date),
                      ('state', 'in',
                          ('waiting', 'confirmed', 'assigned',
                           'partially_available'))]
            if initial_date:
                domain.append(initial_date)
            moves = move_obj.search(domain)
            product.real_stock = sum(moves.mapped('real_stock'))
            product.virtual_stock = sum(moves.mapped('virtual_stock'))
