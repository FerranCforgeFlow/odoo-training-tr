# Copyright 2014-2015 Grupo ESOC <www.grupoesoc.es>
# Copyright 2017-Apertoso N.V. (<http://www.apertoso.be>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = "res.partner"
    _order= 'name'

    published_book_ids = fields.One2many('library.book','publisher_id', string="Published Books")
    authored_book_ids = fields.Many2many('library.book', string="Authored Books") # optional: relation='library_book_res_partner_rel'
    count_books = fields.Integer('Number of Authored Books', compute='_compute_count_books')

    @api.depends('authored_book_ids')
    def _compute_count_books(self):
        for r in self:
            r.count_books = len(r.authored_book_ids)


    # CLASS INHERITANCE (EXTENSION)