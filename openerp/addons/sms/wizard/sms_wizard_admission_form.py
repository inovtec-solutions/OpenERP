from openerp.osv import fields, osv
import datetime

class admission_form(osv.osv_memory):

    _name = "admission.form"
    _description = "Print admission form for draft students"
    _columns = {
              "name": fields.char('Student', size=32),
              'fee_type': fields.selection([('normal','Normal'),('sibling','Sibling'),('teacher_son','Teacher Son')], 'Fee Type', required = True),
             }
    _defaults = {
                 'fee_type':'normal',
           }

    def print_form(self, cr, uid, ids, data):
        result = []
        
#         stdobj = self.pool.get('sms.student').browse(cr, uid, data['active_id'] )
#         std_id =  stdobj.id
#         for f in self.browse(cr, uid, ids):
#             print "student found"
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.student',
             'form': self.read(cr, uid, ids)[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sms.admissionform.name',
            'datas': datas,
        }
    
    
    
admission_form()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: