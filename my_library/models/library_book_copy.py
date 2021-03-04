from odoo import models, fields

class LibraryBookCopy(models.Model):
    _name = 'library.book.copy'
    _inherit = "library.book"
    _description = 'Library Book Copy'

    # By using _name with the _inherit class attribute at the same time, you can copy the
    # definition of the model. When you use both attributes in the model, Odoo will copy the
    # model definition of _inherit and create a new model with the _name attribute.
    # PROTOTYPE INHERITANCE


