# Copyright 2020 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, tools


class StockInventoryProductVersionReport(models.Model):
    _name = "stock.inventory.product.version.report"
    _auto = False

    name = fields.Many2one(comodel_name='stock.move',
                                  string='Name')
    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Version")
    location_id = fields.Many2one(comodel_name="stock.location",
                                  name="Location")
    product_qty = fields.Float(string="Qty")
    real_in_product_qty = fields.Float(string="Real in Qty")
    real_out_product_qty = fields.Float(string="Real out Qty")
    virtual_in_product_qty = fields.Float(string="Virtual in Qty")
    virtual_out_product_qty = fields.Float(string="Virtual out Qty")
    sale_id = fields.Many2one(comodel_name='sale.order.line',
                                  string='Sale')
    purchase_id = fields.Many2one(comodel_name='purchase.order.line',
                                string='Purchase')
    mrp_id = fields.Many2one(comodel_name='mrp.production',
                             string='Production')

    @api.model_cr
    def init(self):
        """ Event Question main report """
        tools.drop_view_if_exists(self._cr,
                                  'stock_inventory_product_version_report')
        self._cr.execute(""" CREATE VIEW 
        stock_inventory_product_version_report AS (
            SELECT
                min(ml.id) as id,
                ml.product_version_id as product_version_id,
                ml.location_id,
                sum(ml.real_in + ml.real_out + ml.virtual_in + 
                ml.virtual_out) as product_qty,
                sum(ml.real_in) as real_in_product_qty,
                sum(ml.real_out) as real_out_product_qty,
                sum(ml.virtual_in) as virtual_in_product_qty,
                sum(ml.virtual_out) as virtual_out_product_qty
            FROM
                stock_move as ml
            GROUP BY
                ml.product_version_id, ml.location_id)""")

    # @api.model_cr
    # def init(self):
    #     """ Event Question main report """
    #     tools.drop_view_if_exists(self._cr, 'event_question_report')
    #     self._cr.execute(""" CREATE VIEW event_question_report AS (
    #         SELECT
    #             att_answer.id as id,
    #             att_answer.event_registration_id as attendee_id,
    #             answer.question_id as question_id,
    #             answer.id as answer_id,
    #             question.event_id as event_id
    #         FROM
    #             stock_move as sm
    #         LEFT JOIN
    #             mrp_production as mp ON sm.production_id = mp.id
    #         LEFT JOIN
    #             event_question as question ON question.id = answer.question_id
    #         GROUP BY
    #             attendee_id,
    #             event_id,
    #             question_id,
    #             answer_id,
    #             att_answer.id
    #     )""")