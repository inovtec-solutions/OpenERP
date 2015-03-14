
import time

from openerp.report import report_sxw

class sms_report_filled_admission_form(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_filled_admission_form, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'print_form': self.print_form,
            'company_name': self.company_name,
            'get_logo': self.get_logo,
            'company_address': self.company_address,
        })
        self.base_amount = 0.00
    
    def company_name(self, data):  
        company = self.pool.get('smsfee.classes.fees').get_company(self.cr, self.uid,self.uid)
        return company
    
    def company_address(self, data):  
        company = self.pool.get('smsfee.classes.fees').get_company(self.cr, self.uid,self.uid)
        street = company.rml_header2
        print "address:",street
        return street
    
    def get_logo(self, data):  
        cpm_id = self.pool.get('res.users').browse(self.cr,self.uid,self.uid).company_id.id
        logo = self.pool.get('res.company').browse(self.cr,self.uid,self.uid).logo_web
        print "logo:",logo
        return logo
    
    def print_form(self, form):
        result = []
        rec = self.pool.get('sms.student').browse(self.cr, self.uid,self.ids[0])
        mydict = {'name': rec.name,'father':rec.father_name,'gender': rec.gender,
                  'dob':rec.birthday,'cellno':rec.cell_no,'phone':rec.phone,'street':rec.cur_address,
                  'city':rec.cur_city,'country':rec.cur_country.name,'email':rec.email,'prev_school':rec.previous_school,
                  'reson_leaving':rec.reason_leaving,'desired_cls':rec.desired_class}
       
        result.append(mydict)
        return result
    
    
report_sxw.report_sxw('report.sms.admissionformfilled.name', 'sms.student', 'addons/sms/rml_filled_admission_form.rml',parser = sms_report_filled_admission_form, header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

