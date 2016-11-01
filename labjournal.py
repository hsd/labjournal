# -*- encoding: utf-8 -*-
# Model of labjournal object
# Copyright (C) 2012  Marcel van der Boom <marcel@hsdev.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#
import logging
logger = logging.getLogger(__name__)

from openerp import models, fields

import time

#from mx.DateTime import *

from datetime import datetime
from datetime import date
from datetime import timedelta

#
# Labjournals are created for different purposes
#
class labjournal_purpose(models.Model):
    _name        = 'labjournal.purpose'
    _description = 'Labjournal purposes'

    # Fields definitions
    name = fields.Char(size=256, required=True, translate=True)
    active = fields.Boolean(default= lambda *a: 1)
    description = fields.Text()
    save_period = fields.Integer(string='Archive period in days', required=True)

    _sql_constraints = [
        ('name', 'UNIQUE(name)', 'Each labjournal purpose must have a unique name')
    ]


#
# Labjournals main model
#
class labjournal_labjournal(models.Model):
    _name        = 'labjournal.labjournal'
    _description = 'Labjournals'

    # Data model
    name    = fields.Char(size=256, required=True, translate=True)
    active  = fields.Boolean()
    purpose = fields.Many2one('labjournal.purpose',
                               required=True,
                               ondelete='restrict')

    owner   = fields.Many2one('res.partner',
                               required=True,
                               ondelete='restrict')
    use_start  = fields.Date('Start of use')
    use_end    = fields.Date('End of use')
    expiration = fields.Date('Expiration date')
    removal    = fields.Date('Removal date')
    production_lots = fields.Many2many('stock.production.lot')

    _defaults = {
        'active'      : lambda *a: 1,
        'name'        : lambda obj, cr, uid, context: '/',
        'use_start'   : lambda *a: time.strftime('%Y-%m-%d')
    }
    _sql_constraints = [
        ('name',     'UNIQUE(name)', 'Each labjournal must have a unique identifier'),
    ]

    # Create a labjournal sequence
    def get_labjournal_seq(self, cr, uid, context={}):
        sequence = self.pool.get('ir.sequence').get(cr, uid, 'labjournal.labjournal')
        return sequence

    # Expiration date calculation based on start date and nr of days defined in the purpose record
    def get_expiration_date(self, start, nrofdays):
        return (DateTimeFrom(start) + RelativeDateTime(days=+nrofdays)).Format('%Y-%m-%d')
    
    # The expiration date is determined by the purpose of the lab journal.
    def set_expiration(self, cr, uid, ids, use_end, purpose, context):
        res = {}
        if use_end and purpose:
            purpose = self.pool.get('labjournal.purpose').browse(cr,uid,purpose, context)
            res = {'value' : {'expiration' : self.get_expiration_date(use_end, purpose.save_period)}}
        return res
        
    # When use_end changes, update expiration date
    def onchange_use_end(self, cr, uid, ids, use_end, purpose, context={}):
        return self.set_expiration(cr, uid, ids, use_end, purpose, context=context)

    # When the purpose changes, the expiration date should also change
    # TODO: really?, or only change it when it has no value yet?
    def onchange_purpose(self, cr, uid, ids, use_end, purpose, context={}):
        return self.set_expiration(cr, uid, ids, use_end, purpose, context=context)

    # We try to get consecutive labjournal numbers, therefore we reserve the sequence 
    # number only at create time and not in the 'new' stage. This prevents burning through
    # sequence numbers a bit, at the expense of a slighttly less intuitive user interface
    def create(self, cr, user, vals, context = None):
        # If name column has '/' value or is not in the set, create a
        # value, otherwise, just do the regulare create method
        if ('name' not in vals) or (vals.get('name')=='/'):
            vals['name'] = self.get_labjournal_seq(cr, user, context)
        return super(labjournal_labjournal,self).create(cr, user, vals, context)


# Make the relation to production lots bidirectional
# so we can reference both objects from both sides.
class stock_production_lot(models.Model):
     _inherit = 'stock.production.lot'

     labjournals = fields.Many2many('labjournal.labjournal')

#
# Override the display of partner addresses in the views of this
# module, so we don't get the whole address in the view.
# TODO: before save this is not doing the right thing yet
# class res_partner_address(models.Model):
#     _inherit="res.partner.address"

#     def name_get(self, cr, user, ids, context=None):
#         # Test the context, if labjournal is true, return our format, else do the normal thing
#         # TODO: commented it out, so it changes it in all places, which is not that bad in our case, but we
#         # really should place this in a WINAP profile then.
#         # if not 'labjournal' in context:
#         return super(res_partner_address, self).name_get(cr, user, ids, context=context)
#         res = []
#         for r in self.read(cr, user, ids, ['name','partner_id']):
#             addr = r['partner_id'][1]
#             if r['name'] :
#                 # Format: Name of person (if any), Name of partner (always there).
#                 addr = r['name'] + ', ' + addr
#             res.append((r['id'], addr.strip() or '/'))
#         return res
