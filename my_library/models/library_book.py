from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import UserError
# This function is used to mark a string as translatable, and to retrieve the translated string at runtime,
# given the language of the end user that's found in the execution context
from odoo.tools.translate import _

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
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')], 'State', default='draft')
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

    # Helper method to check whether a state transition is allowed
    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
               ('available', 'borrowed'),
               ('borrowed', 'available'),
               ('available', 'lost'),
               ('borrowed', 'lost'),
               ('lost', 'available')]
        return (old_state, new_state) in allowed

    #Method to change the state of some books to a new state that i spassed as an argument
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    # Methods to change the book state by calling the change_state method:
    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    # When writing a new method, if you don't use any decorator, then the method is executed
    # on a recordset. In such methods, self is a recordset that can refer to an arbitrary number
    # of database records (this includes empty recordsets), and the code will often loop over the
    # records in self to do something on each individual record
    # The @ api.model decorator is similar, but it's used on methods for which only the model

    def get_all_library_members(self):
        # This is an empty recordset of model library.member
        library_member_model = self.env['library.member']
        # The env attribute of any recordset, available as self.env , is an instance of the Environment class defined in the odoo.api module.
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True

    #UPDATE VALUES OPTION 1
    def change_release_date(self):
        # The method starts by checking whether the book recordset that's passed as self contains exactly one record
        # This is necessary because we don't won't to change the date of multiple records. If you want to update
        # multiple values, you can remove ensure_one() and update the attribute using a loop on the recordset.
        self.ensure_one()
        self.date_updated = fields.Date.today()
    '''
    
    UPDATE VALUES OPTION 2 is to use the update() method by passing dictionary mapping field names to the values you want to set. 
    It can save some typing when you need to update the values of several fields at once on the same record
    def change_update_date(self):
        self.ensure_one()
        self.update({
            'date_release': fields.Datetime.now(),
            'another_field': 'value'
                ...
        })
     '''

    '''
    UPDATE VALUES OPTION 3 is to call the write() method, passing a dictionary that maps the field names to the values 
    you want to set. This method works for recordsets of arbitrary size and will update all records with the specified 
    values in one single database operation when the two previous options perform one database call per record and per field.
    Also, it requires a special format when writing relational fields, similar to the one used by the create() method:
    
        - (0,0,dict_val): creates a new record that will be related to the main record
        - (1,id,dict_val): updates the related record with the specified ID with the values supplied
        - (2,id): removes the record with the specified ID from the related records and deletes it from the database
        - (3,id): removes the record with the specified ID from the related records and it is not deleted from the database
        - (4,id): adds an existing record with the supplied ID to the list of related records
        - (5, ): removes all related records, equivalent to calling (3,id) for each related id
        - (6,0,id_list): creates a relation between the record being updated and the existing record, whose ID are in the
                         Python list called id_list
                         
    Operation types 1 , 2 , 3 , and 5 cannot be used with the create() method.            
    '''

    # We said previously that the search() method returned all the records matching the domain. This is not actually
    # completely true. The security rules ensure that the user only gets those records to which they have read access rights.
    def find_book(self):
        domain = ['|','&', ('name', 'ilike', 'Book Name'),('category_id.name', 'ilike', 'Category Name'),
             '&', ('name', 'ilike', 'Book Name 2'),('category_id.name', 'ilike', 'Category Name 2')]
        books = self.search(domain)


    # FILTER RECORDSET
    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Books: %s', filtered_books)

    # All the records for which the predicate function evaluates to True are added to this empty recordset.
    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
            return False
        return all_books.filter(predicate)

    # the category name by travesing through the Many2one field's category_id as follows: book.category_id.name.
    # However, when working with recordsets with more than one record, the attributes cannot be used.
    @api.model
    def get_author_names(self, books):
        return books.mapped('authors_id.name')
    # For each field in the path, mapped() produces a new recordset that contains all the records related by this field
    # to all elements in the current recordset, and then the next element in the path applies to that new recordset.

    @api.model
    def sort_books_by_date(self, books):
        return books.sorted(key='release_date') #Optional: reverse=True to return a recordset in reverse order


