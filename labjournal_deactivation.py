import wizard

#
# Action which deactivates labjournals, based on the given data
#
def action_deactivation(self, cr, uid, data, context):
    return True
#
# Declare the wizard interface; init->end : call action_deactivation()
#
class labjournal_deactivate(wiz.interface):
    states = {
        'init' : {
            'actions' [],
            'result' : {
                'type' : 'action', 'action': action_deactivation(), 'state':'end'}
                }
            }
        }
labjournal_deactivate()
