from openerp.osv import fields, osv
import datetime
import xlrd


class load_student_wizard(osv.osv_memory):
    """Use this wizard to load students from the excel file"""
    _name = "load.student.wizard"
    _description = "withdraws student from the school"
    _columns = {
              'load_type': fields.selection([('student','Load Student'),('teacher','Load Teacher')],'Load Type', required = True),
             }
    _defaults = {
           }
  
    def load_students(self, cr, uid, ids, context=None):
        
        current_obj = self.browse(cr, uid, ids, context=context)
        if current_obj[0].load_type == "student":
            workbook = xlrd.open_workbook('/home/emaan/records.xls')
            worksheet = workbook.sheet_by_name('Student')
            rows = worksheet.nrows - 1
            cells = worksheet.ncols - 1
            row = 7
            while row < rows:
#                 print "worksheet.cell_value(row, 0),: ", worksheet.cell_value(row, 1)
                print "worksheet.cell_value(row, 0),: ", worksheet.cell_value(row, 6)
                
                sql = """SELECT id from sms_academiccalendar 
                where class_id = (SELECT id from sms_classes where sms_classes.desc = '""" + str(worksheet.cell_value(row, 6)).strip() + """')"""
                cr.execute(sql)
                print sql
                academic_id = cr.fetchone()[0]
                
                print "academic_id,: ", academic_id 
                
            
                student_id = self.pool.get('sms.student').create(cr, uid, {
                    'registration_no': str(academic_id) + "-" +  str(worksheet.cell_value(row, 1)),
                    'name': worksheet.cell_value(row, 3),
                    'father_name': worksheet.cell_value(row, 4),
                    'gender': worksheet.cell_value(row, 5),
                    'father_nic': worksheet.cell_value(row, 8),
                    'phone': worksheet.cell_value(row, 9),
                    'cell_no': worksheet.cell_value(row,10),
                    'cur_address': str(worksheet.cell_value(row, 11)) + ", " + str(worksheet.cell_value(row, 12)) + ", " + str(worksheet.cell_value(row, 13)),
                    'cur_city': 'Peshawar', 
                    'cur_country': 179,
                    'permanent_address': str(worksheet.cell_value(row, 11)) + ", " + str(worksheet.cell_value(row, 12)) + ", " + str(worksheet.cell_value(row, 13)),
                    'permanent_city': 'Peshawar', 
                    'permanent_country': 179, 
                    'admitted_to_class': academic_id,
                    'previous_school': worksheet.cell_value(row, 17),
                    'blood_grp': worksheet.cell_value(row, 19),
                    'birthday': worksheet.cell_value(row, 18),
                    'state': 'Admitted',
                    'admitted_on': '2013-12-01', 
                    'fee_type': worksheet.cell_value(row, 20), }, context=context)
                
                
                student_semester_id = self.pool.get('sms.academiccalendar.student').create(cr, uid, {
                    'name': academic_id,
                    'std_id': student_id,
                    'state': 'Current', 
                    'date_registered': '2013-04-01',}, context=context)
                
                registration_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr, uid, student_semester_id,context = None)
                self.pool.get('sms.student').write(cr, uid, student_id, {'registration_no': registration_no})
                
                subject_ids = self.pool.get('sms.academiccalendar.subjects').search(cr, uid, [('academic_calendar','=', academic_id)], context=context)
                subject_objects = self.pool.get('sms.academiccalendar.subjects').browse(cr, uid, subject_ids, context=context)
                
                for subject in subject_objects: 
                    self.pool.get('sms.student.subject').create(cr, uid, {
                        'student': student_semester_id,
                        'subject': subject.id,
                        'subject_status': 'Current',}, context=context)       
    
                row += 1
            return {}
        
        else:
            workbook = xlrd.open_workbook('/home/emaan/records.xls')
            worksheet = workbook.sheet_by_name('Teacher')
            rows = worksheet.nrows - 1
            cells = worksheet.ncols - 1
            row = 8
            while row < rows:
#                 print "worksheet.cell_value(row, 0),: ", worksheet.cell_value(row, 1)
                print "worksheet.cell_value(row, 0),: ", worksheet.cell_value(row, 6)
                
                student_id = self.pool.get('hr.employee').create(cr, uid, {
                    'name_related': worksheet.cell_value(row, 1),
                    'identification_id': worksheet.cell_value(row, 3),
                    'gender': worksheet.cell_value(row, 5),
                    'mobile_phone': worksheet.cell_value(row,6),
                    'work_email': worksheet.cell_value(row, 7), 
                    'cur_country': 179,
                    'city': 'Peshawar', 
                    'country_id': 179, 
                    'birthday': worksheet.cell_value(row, 10),}, context=context)

                row += 1
            return {}

load_student_wizard()

