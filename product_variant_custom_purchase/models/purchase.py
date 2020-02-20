# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_approve(self, force=False):
        for line in self.order_line:
            product_version = line.product_id._find_version(
                line.custom_value_ids)
            if product_version:
                line.product_version_id = product_version
            else:
                custom_value_ids = []
                name = ""
                for custom in line.custom_value_ids:
                    if custom.custom_value:
                        custom_value_ids.append((0, 0, {
                            'attribute_id': custom.attribute_id.id,
                            'value_id': custom.value_id.id,
                            'custom_value': custom.custom_value,
                        }))
                        if name:
                            name = "{}, ({}):{}".format(
                                name, custom.value_id.name, custom.custom_value
                            )
                        else:
                            name = "({}):{}".format(
                                custom.value_id.name, custom.custom_value)
                product_version = self.env["product.version"].create({
                    'product_id': line.product_id.id,
                    'name': name,
                    'custom_value_ids': custom_value_ids,
                })
                line.product_version_id = product_version
        return super().button_approve()


class PurchaseOrder(models.Model):
    _inherit = "purchase.order.line"

    product_version_id = fields.Many2one(comodel_name="product.version",
                                         name="Product Version")
    version_value_ids = fields.One2many(
        comodel_name="product.version.line",
        related="product_version_id.custom_value_ids")
    custom_value_ids = fields.One2many(
        comodel_name="purchase.version.custom.line", string="Custom Values",
        inverse_name="line_id", copy=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super().onchange_product_id()
        self.custom_value_ids = self._set_custom_lines()
        self.product_version_id = False
        self.name = self._get_purchase_line_description()
        return res

    def _set_custom_lines(self):
        if self.product_version_id:
            return self.product_version_id.get_custom_value_lines()
        elif self.product_id:
            return self.product_id.get_custom_value_lines()


    def _get_purchase_line_description(self):
        if not self.product_id:
            return
        product_lang = self.product_id.with_context(
            lang=self.partner_id.lang,
            partner_id=self.partner_id.id,
        )
        self.name = product_lang.display_name or ""
        version_description = " "
        for value_line in self.custom_value_ids:
            version_description += "[{}: {}({})]".format(
                value_line.attribute_id.name, value_line.value_id.name,
                value_line.custom_value)
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase
        return self.name + version_description

    @api.onchange('product_version_id')
    def product_version_id_change(self):
        for value in self.custom_value_ids:
            self.custom_value_ids = [(2, value)]
        if self.product_version_id:
            self.product_id = self.product_version_id.product_id
            self.name = self._get_purchase_line_description()
        self.custom_value_ids = self._set_custom_lines()

    @api.onchange('custom_value_ids')
    def onchange_version_lines(self):
        product_version = self.product_id._find_version(
            self.custom_value_ids)
        self.product_version_id = product_version
        self.name = self._get_purchase_line_description()


class PurchaseVersionCustomLine(models.Model):
    _inherit = "version.custom.line"
    _name = "purchase.version.custom.line"

    line_id = fields.Many2one(comodel_name="purchase.order.line")
