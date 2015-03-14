from openerp.osv import fields, osv
import datetime

class certificate_form(osv.osv_memory):

    _name = "certificate.form"
    _description = "Print certificate form for draft students"
    _columns = {
              'name': fields.many2one('sms.student','Student Name', required=True),
              'certificate_type': fields.selection([('School Leaving Certificate', 'School Leaving Certificate'),('Sports Certificate', 'Sports Certificate'),('Course Completion Certificate', 'Course Completion Certificate'),('Character Certificate', 'Character Certificate')], 'Certificate Type', required=True),
             }
    _defaults = {
                 'certificate_type':'School Leaving Certificate',
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
             'model': 'sms.student.clearance',
             'form': self.read(cr, uid, ids)[0]
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'sms.certificateform.name',
            'datas': datas,
        }
    
    
    
certificate_form()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: