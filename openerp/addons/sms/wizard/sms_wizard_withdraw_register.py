from openerp.osv import fields, osv
import datetime

class sms_withdraw_register(osv.osv_memory):
    """Use this wizard to withdraw student from the school, cases may be student (struck_off,admission cancel,slc,deceased)"""
     
    def _get_student(self, cr, uid, ids):
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id
    
    _name = "sms.withdraw.register"
    _description = "withdraws student from the school"
    _columns = {
              'session_id': fields.many2one('sms.session', 'Session', help="Select a session",required = True),
              'class_cat': fields.selection([('Primary','Primary'),('Middle','Middle'),('High','High')],'Category', required = True),
             }
    _defaults = {
           }

    def print_list(self, cr, uid, ids, data):
        result = []
        
            
        
        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.studentlist',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'sms.withdraw.register.name',
            'datas': datas,
        }
    
sms_withdraw_register()

