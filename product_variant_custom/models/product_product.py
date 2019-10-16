# Copyright 2019 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_version_ids = fields.One2many(comodel_name='product.version',
                                          inverse_name='product_id')
    product_version_count = fields.Integer(string="Versions",
                                           compute="compute_product_versions")

    @api.depends('product_version_ids')
    def compute_product_versions(self):
        for product in self:
            product.product_version_count = len(product.product_version_ids)

    @api.multi
    def get_custom_attributes(self):
        custom_attributes = []
        for product in self:
            for line in product.attribute_line_ids:
                if line.value_ids.filtered(lambda x: x.is_custom):
                    custom_attributes.append(line.attribute_id.id)
        return custom_attributes

    @api.model
    def _build_attributes_domain(self, version_id, custom_values):
        domain = []
        cont = 0
        assert len(self) == 1, _("Multiple products or none in _find_version "
                                 "method")
        domain.append(('product_version_id', '=', version_id.id))
        if len(custom_values) > 1:
            domain.extend(['|' for i in range(len(custom_values) - 1)])
        for custom_value in custom_values:
            if isinstance(custom_value, dict):
                value_id = custom_value.get('value_id')
            else:
                value_id = custom_value.value_id.id
            if value_id:
                domain.extend(['&', ('value_id', '=', value_id),
                              ('custom_value', '=',
                               custom_value.custom_value)])
                cont += 1
        return domain, cont

    @api.model
    def _find_version(self, custom_values):
        if self:
            versions = self.env['product.version'].search(
                [('product_id', '=', self.id)])
            version_line_obj = self.env['product.version.line']
            for version in versions:
                domain, cont = self._build_attributes_domain(
                    version, custom_values)
                custom_lines = version_line_obj.search(domain)
                if len(custom_lines) == cont:
                    return version
        return False