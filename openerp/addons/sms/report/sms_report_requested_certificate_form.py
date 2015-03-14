
import time
from datetime import date
from openerp.report import report_sxw
from dateutil import parser
import datetime

class crossovered_analytic(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(crossovered_analytic, self).__init__(cr, uid, name, context = context)
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
        rec = self.pool.get('sms.student.clearance').browse(self.cr, self.uid,self.ids[0])
        
        for obj in rec.certificate:
            print "Certificate Name: ", obj.text
#             formate = str(obj.text)
#             formate = formate.replace("<name>", rec.name.name)
#             formate = formate.replace("<father_name>", rec.name.father_name)
#             formate = formate.replace("<degree>", rec.name.current_class.name)
#             formate = formate.replace("<exam_date>", 'November 17, 2014')
#             formate = formate.replace("<type>", 'Regular')
#             formate = formate.replace("<obtained_marks>", '800')
#             formate = formate.replace("<total_marks>", '850')
#             formate = formate.replace("<grade>", 'A+')
#             #Now to get all the relevant subject of this student. Since we have already used rec.name.current_class above so, extract subject ids from with the help of this from sms.academiccalendar.subjects object.
            subject_ids = self.pool.get('sms.academiccalendar.subjects').search(self.cr, self.uid,[('academic_calendar','=',rec.name.current_class.id)])
#             #Now on the basis of ids, select all subjects from sms.academiccalendar.subjects object 
            subject_obj = self.pool.get('sms.academiccalendar.subjects').browse(self.cr, self.uid,subject_ids)
             #To mention your own serial no. with each subject, use this
            i = 1
            sub_str = ".\n"
            for sub in subject_obj:
                if i%3 == 0: #it will restrict loop to print only 3 subject per line
                     sub_str = sub_str + str(i) + ". "+ str(sub.name) + "\n\n"
                else:
                     sub_str = sub_str + str(i) + ". "+ str(sub.name) + "  "
                i = i + 1
             #Now mention where these subjects will be placed? So below code will replace the <subjects> tag will all selected/extracted subjects of current student   
#             formate = formate.replace("<subjects>", sub_str)
            # To extract birthday of the selected student,  ('%B %d, %Y') date format, else will display "Birthday Missing" if birthday is not entered for student
#             if rec.name.birthday:
#                my_date = parser.parse(rec.name.birthday) 
#                 formate = formate.replace("<date_of_birth>", my_date.strftime('%B %d, %Y'))
#             else:
#                 formate = formate.replace("<date_of_birth>", "Birthday Missing")
            
            mydict = {'name': rec.name.name,'father':rec.father_name, 'certificate':obj.name, 'degree':rec.name.current_class.class_id.name, 'registration_key':rec.name.registration_no, 'date_of_birth':datetime.datetime.strptime(str(rec.name.birthday), '%Y-%m-%d').strftime('%d-%B-%Y'), 'subjects':sub_str, 'obtained_marks':'800', 'total_marks':'850','grade':'A', 'approved_by':rec.approved_by.name,'issued_by':rec.issued_by.name,
                  'date_issued':datetime.datetime.strptime(str(rec.date_issued), '%Y-%m-%d').strftime('%d-%B-%Y')}
            result.append(mydict)
        return result
    
    
report_sxw.report_sxw('report.sms.certificaterequested.name', 'sms.student.clearance', 'addons/sms/rml_requested_certificate_form.rml',parser = crossovered_analytic, header='external')
report_sxw.report_sxw('report.sms.sportscertificate.name', 'sms.student.clearance', 'addons/sms/rml_sports_certificate_form.rml', parser = crossovered_analytic, header='external')
#3
#4
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

