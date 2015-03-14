from openerp.osv import fields, osv
import datetime

class class_fee_receipts_unpaid(osv.osv_memory):
    
    def _get_class(self, cr, uid, ids):
        
        obj = self.browse(cr, uid, ids['active_id'])
        std_id =  obj.id
        return std_id
    
    _name = "class.fee.receipts.unpaid"
    _description = "admits student in a selected class"
    _columns = {
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", help="Class"),
              'today': fields.date('Date'),
              'helptext':fields.text('helptext')
               }
    _defaults = {
                 'class_id':_get_class,
                 'helptext':'Print Monthly Fee Receipts:\n1: If Fee Register is not update, first update fee Register..\n2: Unpaid due are included till corrent month.\n3:To Print receipt for a single student,use option on student form.'
           }
    
    def print_fee_report(self, cr, uid, ids, data):
        result = []
        thisform = self.read(cr, uid, ids)[0]
        report = 'smsfee_unpaidfee_receipt_name'        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
        }
                
class_fee_receipts_unpaid()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: