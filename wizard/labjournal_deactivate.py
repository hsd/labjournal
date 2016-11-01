import time
from openerp import models, fields

import logging
logger = logging.getLogger(__name__)


#
# Object to handle deactivation of labjournals
#
# The logic for deactivation is as follows:
# - given a subset of labjournals which have an use_end date
# - set Active to False, Set 'Removal date' to today fo the selected labjournal
class labjournal_deactivate(models.TransientModel):
    _name = 'labjournal.deactivate'
    _description = 'Handle deactivation of labjournals'

    #
    # Deactivate labjournals, based on the data passed in
    #
    def _action_deactivate_labjournals(self, cr, uid, ids, context):
        # What to do here, the work is done in the create method?
        return {}

    def _get_selected_journals(self, cr, uid, context=None):
        res = []
        lj_obj = self.pool.get('labjournal.labjournal')
        for lj in lj_obj.browse(cr, uid, context['active_ids']):
            if lj.use_end:
                # The labjournal has ended usage, consider it
                res.append(lj.id)
        # Return just the id's, which
        return res

    # Fill the defaults with the selected records
    def _get_labjournal_ids(self, cr, uid, ids, fname, arg, context=None):
        # When nothing else is available the 'own' id of the current
        # 'deactivate object' is 1, so return the active ids for deactivation.
        return {'1': context['active_ids']}

    # Subset of
    labjournals = fields.Many2many('labjournal.labjournal')


    _defaults = {
        'labjournal_ids' : _get_selected_journals
        }

    # On create, run deactivation for all values in labjournal_ids, that's it
    def create(self, cr, uid, vals, context=None):
        # Handle all the labjournal ids in vals dictionary, if any
        if 'labjournal_ids' in vals and vals['labjournal_ids'][0][2]:
            lj_ids = vals['labjournal_ids'][0][2]

            # We have ids, update them with removal=today() and Active=False
            upd_values = {
                'removal': time.strftime('%Y-%m-%d'),
                'active': False
                }
            # Write these values to the selected ids
            self.pool.get('labjournal.labjournal').write(cr, uid, lj_ids, upd_values)
        return 1
