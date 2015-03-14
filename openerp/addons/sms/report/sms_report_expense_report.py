
import time

from openerp.report import report_sxw

class sms_wizard_expense_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_wizard_expense_report, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'report_title': self.report_title,
            'expense_list': self.expense_list,
        })
        self.base_amount = 0.00
    
    def report_title(self, data):  
        start_date = self.datas['form']['from_date']
        end_date = self.datas['form']['to_date']
        string = "Expenses From " +str(start_date) + "-TO -"+str(end_date)
        return string
    
    
    
    def expense_list(self, data):   
        result = []
        sql = """SELECT name,id,date,employee_id,user_id,date_valid,user_valid,voucher_id,state
                 FROM hr_expense_expense WHERE  date >='"""+str(self.datas['form']['from_date'])+"""'
                 AND date <='"""+str(self.datas['form']['to_date'])+"""'
                 AND state ='"""+str(self.datas['form']['state'])+"""' ORDER BY hr_expense_expense.date  """
        self.cr.execute(sql)
        rows = self.cr.fetchall()
        total = 0
        my_dict = {'total':'','sub_dict':''}
        result2 = []
        for f in rows:
            amount = self.pool.get('hr.expense.expense').browse(self.cr,self.uid,f[1]).amount
            employee = self.pool.get('hr.employee').browse(self.cr,self.uid,f[3]).name
            valid_by = self.pool.get('res.users').browse(self.cr,self.uid,f[6]).name
            sub_dict = {'id':'','disc':'','dated':'','employee':'','user':'','date_validate':'','valid_by':'','voucher_no':'--','amount':'','state':''}
            sub_dict['id']            =  f[1]
            sub_dict['dated']         =  f[2]
            sub_dict['desc']          =  f[0]
            sub_dict['employee']      =  employee   
            sub_dict['date_validate'] =  f[5]
            sub_dict['valid_by']      =  valid_by
            sub_dict['voucher_no']    =  f[7] 
            sub_dict['state']         =  f[8]
            sub_dict['amount']        =  amount
            total = total + amount
            result2.append(sub_dict)
        my_dict['total'] = total 
        my_dict['sub_dict'] = result2
        result.append(my_dict)
        return result
    
    
report_sxw.report_sxw('report.sms_expense_report_name', 'hr.expense.expense', 'addons/sms/report/sms_report_expense_report.xml',parser = sms_wizard_expense_report, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

