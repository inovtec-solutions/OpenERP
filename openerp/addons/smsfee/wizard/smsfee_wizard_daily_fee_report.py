from openerp.osv import fields, osv
import datetime

class daily_report(osv.osv_memory):

    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
    
    _name = "daily.report"
    _description = "admits student in a selected class"
    _columns = {
              "session": fields.many2one('sms.session', 'Session', help="Select A session , you can also print reprts from previous session."),
              'fee_manager':fields.many2one('res.users', 'Fee Manager',  help="Select A Fee Manager to check his fee collection.Leave it blank if you want to print for all Managers."),
              "class_id": fields.many2one('sms.academiccalendar', 'Class', domain="[('fee_defined','=',1)]", help="Select A class to check its fee collection.Leave it blank if you want to print for all classes"),
              'from_date': fields.date('From'),
              'to_date': fields.date('To'),
               }
    _defaults = {
                 'session':_get_active_session,
           }
    
    def print_daily_report(self, cr, uid, ids, data):
        result = []
        thisform = self.read(cr, uid, ids)[0]
        
 
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'smsfee.classfees.register',
             'form': self.read(cr, uid, ids)[0],
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':'smsfee.dailyfee.report.name',
            'datas': datas,
        }
                
daily_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: