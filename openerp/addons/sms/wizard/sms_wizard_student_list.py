from openerp.osv import fields, osv
import datetime
import xlwt
import socket
import fcntl
import struct
from struct import pack, unpack

class sms_student_list(osv.osv_memory):

    _name = "sms.studentlist"
    _description = "will print student list"
    _columns = {
              'acad_cal':fields.many2one('sms.academiccalendar','Academic Calendar',domain = [('state','=','Active')] ),
              'list_type': fields.selection([('contact_list','Contact list'),('check_admissions','Check Admissions')], 'List Type', required = True),
              'start_date': fields.date('Start Date'),
              'end_date':fields.date('End Ddate'),
              'export_to_excel':fields.boolean('Save As MS Excel File')
             }
    _defaults = {
           }

    def print_list(self, cr, uid, ids, data):
        result = []
        thisform = self.browse(cr, uid, ids)[0]
        listtype = thisform['list_type']
        if listtype == 'check_admissions':
            report = 'sms.std_admission_statistics.name'
        
        elif listtype =='contact_list':
            student_cal_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',thisform['acad_cal'].id)])
            if not student_cal_ids:
                raise osv.except_osv(('Student Not Found'),('No Student exists in selected class.'))
            student_rows =  self.pool.get('sms.academiccalendar.student').browse(cr,uid,student_cal_ids)

            if thisform['export_to_excel']:
                book=xlwt.Workbook()
                sheet1=book.add_sheet('Sheet 1',cell_overwrite_ok=True)
                title="""ABC"""
                program_name = ""
                title="""Student List of """
                column=['SNO','Candidate No','Name','Father Name','Gender','Domicile','Blood Group','Nationality','Date of Birth','Current Address','LandLineNo','Cell No','Email']
                sheet1.write_merge(r1=0, c1=0, r2=0, c2=11, label=title)
                col=0
                row = 2
                for i in column:
                    sheet1.write(row,col,i)
                    col+=1
                
                i = 1;
                row = row + 1 
                for student_row in student_rows:
                    ##################################################################################
                    sheet1.write(row,0,i)
                    sheet1.write(row,1, str(student_row.std_id.registration_no))
                    sheet1.write(row,2, str(student_row.std_id.name))
                    sheet1.write(row,3, str(student_row.std_id.father_name))
                    sheet1.write(row,4, str(student_row.std_id.gender))
                    sheet1.write(row,5, str(student_row.std_id.domocile))
                    sheet1.write(row,6, str(student_row.std_id.blood_grp))
                    sheet1.write(row,7, str(student_row.std_id.cur_country.name))
                    sheet1.write(row,8, str(student_row.std_id.birthday))
                    sheet1.write(row,9, str(student_row.std_id.cur_address))
                    sheet1.write(row,10, str(student_row.std_id.phone))
                    sheet1.write(row,11, str(student_row.std_id.cell_no))
                    sheet1.write(row,12, str(student_row.std_id.email))
                                               
                    row+=1
                    i+=1
                
                location="/var/www/excel/"
                if student_rows:
                    filename= student_rows[0].name.name  + ": StudentList.xls"
                else:
                    filename= "StudentList.xls"
                
                self.file_name=filename
                strs=str(location)+str(filename)
                book.save(strs)
                
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ip = socket.inet_ntoa(fcntl.ioctl(
                    s.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', 'wlan0'[:15])
                )[20:24])
                url = 'http://'+ip+'/excel/'+str(filename)       
                
                return {
                'type': 'ir.actions.act_url',
                'url':url,
                'target': 'new'
                }
            
            else:
                report = 'sms.studentslist.name'
        datas = {
             'ids': [],
             'active_ids': '',
             'model': 'sms.studentlist',
             'form': self.read(cr, uid, ids)[0],
             }
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,
            }
        
sms_student_list()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: