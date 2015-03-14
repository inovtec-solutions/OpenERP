
import time

from openerp.report import report_sxw

class sms_report_admission_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_admission_form, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'print_form': self.print_form,
        })
        self.base_amount = 0.00
    
    
    def print_form(self, form):
        result = []
        print "method called in report" 
        
        return result
    
    
report_sxw.report_sxw('report.sms.admissionform.name', 'sms.timetable', 'addons/sms/admission_form.rml',parser = sms_report_admission_form, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

