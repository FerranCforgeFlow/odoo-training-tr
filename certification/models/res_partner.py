# Copyright 2014-2015 Grupo ESOC <www.grupoesoc.es>
# Copyright 2017-Apertoso N.V. (<http://www.apertoso.be>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    certification_ids = fields.One2many(comodel_name='certification', inverse_name='owner_id')
    is_certification_body = fields.Boolean(string="It is an entity", default="False", help="Check this box if the contact is a certification entity")