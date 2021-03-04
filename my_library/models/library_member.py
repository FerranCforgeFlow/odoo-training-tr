from odoo import models, fields
from datetime import timedelta

class LibraryBook(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner':'partner_id'}

    partner_id = fields.Many2one('res.partner', ondelete='cascade')

    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')

    # There are cases where, rather than modifying an existing
    # model, we want to create a new model based on an existing one to use the features it
    # already has. We can copy a model's definitions with prototype inheritance, but this will
    # generate duplicate data structures. If you want to copy a model's definitions without
    # duplicating data structures, then the answer lies in Odoo's delegation inheritance
    # Delegation Inheritance only works for fields, and not for methods

    # DELEGATION INHERITANCE

    '''
    _name = 'library.member'
        
    partner_id = fields.Many2one('res.partner', ondelete='cascade', delegate=True)
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')
    
    Instead of creating an _inherits dictionary, you can use the delegate=True attribute in the Many2one 
    field definition this will work exactly like the _inherits option.
    '''
