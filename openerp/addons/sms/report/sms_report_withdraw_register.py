
import time

from openerp.report import report_sxw

class sms_report_withdraw_register(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_withdraw_register, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'report_title': self.report_title,
            'print_withdrawal_register': self.print_withdrawal_register,
        })
        self.base_amount = 0.00
    
    def report_title(self, data):  
        string = "Withdraw Register \n "
        return string
    
    def print_withdrawal_register(self, data):                                                         
        
        print "session"
        
        result = []
        ftlist = []
        this_form = self.datas['form']
        session_id = this_form['session_id'][0]
        print "session ",session_id
        class_cat = this_form['class_cat']
        
#         sql = """SELECT sms_student.id FROM sms_student
#             INNER JOIN sms_academiccalendar
#             ON sms_student.admitted_to_class = sms_academiccalendar.id
#             INNER JOIN sms_classes
#             ON sms_academiccalendar.class_id = sms_classes.id 
#             WHERE sms_student.state != 'Draft'
#             AND sms_student.state != 'admission_cancel'
#             AND sms_student.state != 'drop_out'
#             AND sms_student.state != 'deleted'
#             AND registration_counter = 0
#             AND sms_classes.category = '"""+class_cat+"""'
#             AND sms_academiccalendar.session_id = """ + str(session_id) + """
#             order by admitted_on, sms_student.name"""
#              
#  
#         self.cr.execute(sql)
#         rows = self.cr.fetchall()
#         i = 1
#          
#         session =  self.pool.get('sms.session').browse(self.cr,self.uid,session_id).name
#          
#         for std in rows:
#             admin_no = str(class_cat[:1])+"-"+str(i)+"/"+str(session)
#              
#             sql = """update sms_student set registration_counter = """ +  str(i) + """, 
#                     registration_no = '""" + str(admin_no) + """'
#                     WHERE id = """ + str(std[0])
#             i = i + 1
#              
#             self.cr.execute(sql)
#             self.cr.commit()
#             
#             self.pool.get('sms.registration.nos').create(self.cr, self.uid, {
#                 'student_id': std[0],
#                 'name': admin_no,
#                 'class_category': class_cat,
#                 'is_active': True,})


        sql = """ SELECT sms_academiccalendar.id FROM sms_academiccalendar
                INNER JOIN sms_classes ON
                sms_classes.id = sms_academiccalendar.class_id
                WHERE sms_academiccalendar.session_id = """+str(session_id)+"""
                AND sms_classes.category = '"""+class_cat+"""'"""
             
        self.cr.execute(sql)
        rows = self.cr.fetchall()
        for cls_id in rows:
            ftlist.append(cls_id[0])
        ftlist = tuple(ftlist)
        ftlist = str(ftlist).rstrip(',)')
        ftlist = ftlist+')'
        print "rows:",ftlist
      
        if rows:
            sql2 = """SELECT id from sms_student 
                where admitted_to_class IN"""+str(ftlist) + """ 
                AND sms_student.state != 'deleted'
                order by registration_counter"""
            self.cr.execute(sql2)
            rows2 = self.cr.fetchall()
            sno = 1
            for std in rows2:
                print "std:",std[0]
                std_rec = self.pool.get('sms.student').browse(self.cr, self.uid,std[0])
                if std_rec:
                    mydict = {'sno':'','reg_no':'','student':'','dob':'','father':'','occupation':'','address':'','date_admitted':'--','admitted_to':'--','date_withdraw':'--'}
                    mydict['sno'] = sno
                    mydict['student'] = std_rec.name
                    mydict['dob'] = std_rec.birthday
                    mydict['address'] = str(std_rec.cur_address) + "-"+str(std_rec.cur_city)
                    mydict['father'] = std_rec.father_name
                    mydict['reg_no'] = std_rec.registration_no
                    mydict['date_admitted'] = std_rec.admitted_on
                    mydict['admitted_to'] =self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,std_rec.admitted_to_class.id).name 
                    mydict['date_withdraw'] = std_rec.date_withdraw
                    sno = sno + 1
                    result.append(mydict)
                

        return result
    
        
    
report_sxw.report_sxw('report.sms.withdraw.register.name', 'sms.student', 'addons/sms/rml_withdraw_register.rml',parser = sms_report_withdraw_register, header=None)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

