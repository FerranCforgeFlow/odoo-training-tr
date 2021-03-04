from odoo import models, fields, api
from datetime import timedelta

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    _description = 'Abstract Archive'

    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['base.archive']
    # To sort the records first (from the newest to the oldest, and then by title)
    _order = 'date_release desc, name'
    # To use the short_name field as the record representation
    # In short, _rec_name is thedisplay name of the record used by Odoo GUI to represent that record
    _rec_name = 'short_name'
    # The first step creates a database constraint on the model's table. It is enforced at the database level.
    _sql_constraints = [('name_uniq', 'UNIQUE (name)','Book title must be unique.'),
                        ('positive_page', 'CHECK(pages>0)','Number of pages must be positive')]

    name = fields.Char("Title", required=True)
    date_release = fields.Date("Release Date")
    cost_price = fields.Float("Book Cost", digits='Book Price')
    short_name = fields.Char('Short Title', required=True)
    author_ids = fields.Many2many('res.partner', string="Authors")
    notes = fields.Text('Internal Notes')
    state = fields.Selection(
        [('draft', 'Not Available'),
         ('available', 'Available'),
         ('lost', 'Lost')], 'State')
    description = fields.Html('Description')
    cover = fields.Binary('Book Cover')
    currency = fields.Many2one('res.currency', string="Currency")
    retail_price = fields.Monetary('Retail Price', currency_field='currency')
    out_of_print = fields.Boolean('Out_of_Print?')
    date_updated = fields.Datetime('Last Updated')
    pages = fields.Integer('Number of Pages')
    reader_rating = fields.Float('Reader Average Rating', digits=(14, 4))
    # We access the publisher-related record through publisher_id , and then read its city field
    publisher_id = fields.Many2one('res.partner', string='Publisher') # optional: ondelete='set null',context={},domain=[],
    publisher_city = fields.Char('Publisher City', related='publisher_id.city', readonly=True)
    category_id = fields.Many2one('library.book.category')
    age_days = fields.Float(
        string='Days Since Release',
        compute='_compute_age',
        inverse='_inverse_age',
        search='_search_age',
        # optional: store=False,
        # optional: compute_sudo=True
    )
    # We need to add the reference field and use the previous function (_referencable_models)to provide a list of selectable models
    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')

    def name_get(self):
        result = []
        for record in self:
            rec_name = "%s (%s)" % (record.name, record.date_release)
            result.append((record.id,rec_name))
        return result

    # method with the value computation logic
    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self:
            if book.date_release:
                delta = today - book.date_release
                book.age_days = delta.days
            else:
                book.age_days = 0
    # implement the logic to write on the computed field
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    # implement the logic that will allow you to search in the computed field
    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = {'>': '<', '>=': '<=','<': '>', '<=': '>='}
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]



    # We added a method to perform Python code validation. It is decorated with @api.constrains , meaning that it
    # should be executed to run checks when one of the fields in the argument list is changed
    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
             raise models.ValidationError('Release date must be in the past')

    # We need to add a helper method to dynamically build a list of selectable target models
    # needs the @api.model decorator because it operates on the model level, and not on the record set level.
    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]