from odoo import fields, models, api
from odoo.exceptions import ValidationError

class BookCategory(models.Model):
    _name = 'library.book.category'
    _description = 'Library Book Category'

    #To enable the special hierarchy support
    _parent_store = True
    _parent_name = "parent_id"

    name = fields.Char('Category')
    description = fields.Text('Description')
    parent_id = fields.Many2one('library.book.category', string="Parent Category", ondelete='restrict', index=True)
    #The Many2one relation adds a field to refgerence the parent record
    child_ids = fields.One2many('library.book.category','parent_id',string="Child Categories")
    #The One2many relation does not add any additional fields to the database, but provides a shortcut to
    #access all the records with this record as their parent.
    parent_path = fields.Char(index=True)

    #Prevent cyclic dependencies in the hierarch, which means having a record in both the ascending and descending trees.
    #This is dangerous for programs that anvigate through the tree, since tehy can get into an infinite loop
    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError('Error! You cannot create recursive categories.')

    def create_categories(self):
        # Dictionary of values for the fields of the first child categories
        categ1 = {
            'name': 'Child Category 1',
            'description': 'Description for child 1'
        }
        categ2 = {
            'name': 'Child Category 2',
            'description': 'Description for child 2'
        }
        # Dictionary of values for the fields of the parent category:
        parent_category_val = {
            'name': 'Parent category',
            'email': 'Description for parent category',
            'child_ids': [(0, 0, categ1), (0, 0, categ2)]
        }

        record = self.env['library.book.category'].create(parent_category_val)
        # To create a new record for a model, we can call the create(values) method on any recordset related to the
        # model. This method returns a new recordset with a length of 1 and contains the new record, with the field
        # values specified in the values dictionary.

