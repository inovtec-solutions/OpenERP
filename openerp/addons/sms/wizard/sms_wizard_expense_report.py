from openerp.osv import fields, osv
import datetime
import xlwt

class sms_expense_report(osv.osv_memory):

    _name = "sms.expense.report"
    _description = "will print daily expenses"
    _columns = {
              'from_date':fields.date('From',required = True ),
              'to_date': fields.date('To',required = True ),
              'state': fields.selection([
                ('draft', 'New'),
                ('cancelled', 'Refused'),
                ('confirm', 'Waiting Approval'),
                ('accepted', 'Approved')
                ], required=True),
              'expense_manager':fields.many2one('res.users', 'User',),
             }
    _defaults = {
           }

    def print_expense_list(self, cr, uid, ids, data):
        result = []
        thisform = self.read(cr, uid, ids)[0]
        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'hr.expense.expense',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'sms_expense_report_name',
            'datas': datas,
        }
    
    
sms_expense_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: