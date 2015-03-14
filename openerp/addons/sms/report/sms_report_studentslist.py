
import time

from openerp.report import report_sxw

class sms_report_studentslist(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_report_studentslist, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'report_title': self.report_title,
            'class_name': self.class_name,
            'get_student_contacts': self.get_student_contacts,
            'get_admission_statistics': self.get_admission_statistics,
        })
        self.base_amount = 0.00
    
    def report_title(self, data):  
        start_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['start_date'])
        end_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['end_date'])
               
        string = "Students Admissions \n " +str(start_date) + "-TO -"+str(end_date)
        return string
    
    def class_name(self, data):  
        return self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,self.datas['form']['acad_cal'][0]).name
    
    def get_student_contacts(self, data):                                                         
        
        ###################################################################3
        
#         students = self.pool.get('sms.student').search(self.cr, self.uid,[('registration_no', '!=', None)])
#         print "Total: ", len(students)
#         students = self.pool.get('sms.student').browse(self.cr, self.uid,students)
#         counter = 1
#         counter2 = 1
#         
#         for student in students:
#             if str(student.registration_no).lower().find("h") > -1:
#                 class_category = "High"
#             elif str(student.registration_no).lower().find("m") > -1:
#                 class_category = "Middle"
#             else:
#                 class_category = "Primary"
#            
#             reg_no_exist = self.pool.get('sms.registration.nos').search(self.cr, self.uid,[('name', '=', student.registration_no),('class_category', '=', class_category)])
#             if not reg_no_exist:
#                 self.pool.get('sms.registration.nos').create(self.cr, self.uid, {
#                          'student_id': student.id,
#                          'name': student.registration_no,
#                          'class_category': class_category,
#                          'is_active': True,})
#                 print "Assigned Counter: ", counter
#                 counter = counter + 1
#             else:
#                 #student.current_class.class_id.category
#                 std_class = self.pool.get('sms.academiccalendar.student').search(self.cr, self.uid,[('std_id', '=', student.id),('state', '=', 'Current')])
#                 
#                 if not std_class:
#                     continue
#                 acad_std = self.pool.get('sms.academiccalendar.student').browse(self.cr, self.uid,std_class[0])
#                 category2 = acad_std.name.class_id.category
#                                 
#                 std_reg_type_exist = self.pool.get('sms.registration.nos').search(self.cr, self.uid,[('student_id', '=', student.id),('class_category', '=', category2)])
#                 print "category2: ", category2, "  std_reg_type_exist: ", std_reg_type_exist, "  student_id: ", student.id
#                 if not std_reg_type_exist:
#                     std_reg_nos = self.pool.get('sms.registration.nos').search(self.cr, self.uid,[('student_id', '=', student.id)])
#                     self.pool.get('sms.registration.nos').write(self.cr, self.uid, std_reg_nos, {'is_active':False,})
#                     admn_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(self.cr,self.uid,std_class[0])
# 
#                     self.pool.get('sms.registration.nos').create(self.cr, self.uid, {
#                         'student_id': student.id,
#                         'name': admn_no,
#                         'class_category': category2,
#                         'is_active': True,})
#                     self.pool.get('sms.student').write(self.cr, self.uid, student.id, {'registration_no':admn_no,})
#                     print "Registration No is : ", admn_no
#                     print "Changed Counter2: ", counter2
#                     counter2 = counter2 + 1
                
        ###################################################################3
        
        result = []
        this_form = self.datas['form']
        acad_cal = this_form['acad_cal'][0]
        students = self.pool.get('sms.academiccalendar.student').search(self.cr, self.uid,[('name', '=', acad_cal),('state', '=','Current')])
        
        i = 1
        for idss in students:
            mydict = {'sno':'','admsn_no':'','student':'','father':'','Cellno':'--','phone':'--',}
            row = self.pool.get('sms.academiccalendar.student').browse(self.cr, self.uid,idss)
            mydict['sno'] = i
            mydict['admsn_no'] = row.std_id.registration_no
            mydict['student'] = row.std_id.name
            mydict['father'] = row.std_id.father_name
            mydict['Cellno'] = row.std_id.cell_no
            mydict['phone'] = row.std_id.phone
            i = i + 1
            result.append(mydict)
        return result
    
    def get_admission_statistics(self, data):                                                         
        result = []
        this_form = self.datas['form']
        
        fee_st =tuple(self.pool.get('sms.feestructure').search(self.cr, self.uid,[]))
        acad_cal =tuple(self.pool.get('sms.academiccalendar').search(self.cr, self.uid,[('state', '!=','Closed')]))
        
        sql = """SELECT id FROM sms_academiccalendar
            WHERE ('""" + str(this_form['start_date']) + "' <=  date_started and '""" + this_form['end_date'] + """' >= date_started ) 
            OR ('""" + str(this_form['start_date']) + "' >=  date_started and '""" + this_form['end_date'] + """' <= date_closed ) 
            OR ('""" + str(this_form['start_date']) + "' <=  date_closed and '""" + this_form['end_date'] + """' >= date_closed ) 
            OR state = 'Draft'
            OR date_closed is null""" 
        
        self.cr.execute(sql)
        acad_cal = self.cr.fetchall()
       
        for cls in acad_cal:
            sub_list = []
            obj = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,cls[0])
            mydict = {'acad_cal':'','state':'','list':''}
            mydict['acad_cal'] = obj.name
            mydict['state'] = obj.state
            j = 1
            
            for fs in fee_st:
                inner_dict = {'SNO':'','fee_structure':'','no_admission':''}
                inner_dict['fee_structure'] = self.pool.get('sms.feestructure').browse(self.cr, self.uid,fs).name
                inner_dict['SNO'] = j
                
                sql = """SELECT count(sms_academiccalendar_student.id) FROM sms_student
                    inner join sms_academiccalendar_student on 
                    sms_student.id = sms_academiccalendar_student.std_id
                    WHERE sms_academiccalendar_student.name = """ + str(obj.id) + """ 
                    AND sms_student.fee_type = """ + str(fs) + """
                    AND sms_student.state in ('Admitted','admission_cancel','drop_out','slc') 
                    AND sms_student.admitted_on >= '""" + this_form['start_date'] + """'
                    AND sms_student.admitted_on <='""" + this_form['end_date'] + """'"""
                    
                print sql
                
                self.cr.execute(sql)
                row = self.cr.fetchone()
                inner_dict['no_admission'] = row[0]
                if row[0] > 0:
                    sub_list.append(inner_dict)
                    j = j + 1

            mydict['list'] = sub_list
            if sub_list:
                result.append(mydict)
        return result
    
    
report_sxw.report_sxw('report.sms.studentslist.name', 'sms.student', 'addons/sms/rml_studentslist.rml',parser = sms_report_studentslist, header='internal')
report_sxw.report_sxw('report.sms.std_admission_statistics.name', 'sms.student', 'addons/sms/rml_std_admission_statistics.rml',parser = sms_report_studentslist, header='internal')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

