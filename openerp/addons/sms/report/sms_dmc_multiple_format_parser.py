# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from datetime import datetime

from openerp.report import report_sxw

class sms_dmc_multiple_format_parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sms_dmc_multiple_format_parser, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'get_exam_type': self.get_exam_type,
            'get_class': self.get_class,
            'get_section': self.get_section,
            'get_subject': self.get_subject,
            'get_teacher': self.get_teacher,
            'get_today_formatted':self.get_today_formatted,
            'get_today_month':self.get_today_month,
            
          
            'get_students_dmc':self.get_students_dmc,
            'get_company':self.get_company,
        })
        self.base_amount = 0.00
    
    def get_company(self, objects):
        sql = """SELECT name from res_company where id in (SELECT cid from res_company_users_rel) order by id"""
        self.cr.execute(sql)
        company_name = self.cr.fetchone()[0]
        return company_name
    
    def get_exam_type(self,form):
        return self.pool.get('sms.exam.datesheet').browse(self.cr, self.uid,self.datas['form']['exam_type'][0]).name
        
    def get_class(self,form):
        rec = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,self.datas['form']['academiccalendar_id'][0])
        return rec.class_id.name + '- (Session:'+rec.acad_session_id.name+')'
    
    def get_section(self,form):
        return self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,self.datas['form']['academiccalendar_id'][0]).section_id.name        
    
    def get_subject(self,form):
        return self.pool.get('sms.academiccalendar.subjects').browse(self.cr, self.uid,self.datas['form']['subject_id'][0]).subject_id.name
    
    def get_teacher(self,form):
        return self.pool.get('sms.academiccalendar.subjects').browse(self.cr, self.uid,self.datas['form']['subject_id'][0]).teacher_id.name
            
    def get_today_formatted(self,form):
        
        today = time.strftime('%B %d, %Y')
        return today 
    
    def get_today_month(self,form):
        today = time.strftime('%B %d, %Y')
        today = today.split(" ")[0] + ", " + today.split(" ")[2] 
        return today
     
    
    def get_students_dmc(self,form):
        
        final_result = []
        subjects = []

        dmc_type = str(form['dmc_type'])
        academiccalendar_id = str(form['academiccalendar_id'][0])
        exam_type = str(form['exam_type'][0])
        
        student_query = ""
        if dmc_type == 'Single_DMC':
            student = str(form['student_id'][0])
            student_query = "AND sms_student.id = " + str(student)
           
        student_sql = """SELECT distinct sms_student.id, sms_student.name, sms_student.father_name, sms_student.current_class from sms_student
                    inner join sms_academiccalendar_student on
                    sms_student.id = sms_academiccalendar_student.std_id 
                    inner join sms_student_subject
                    on sms_academiccalendar_student.id = sms_student_subject.student
                    inner join sms_exam_lines
                    on sms_student_subject.id = sms_exam_lines.student_subject
                    WHERE sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted'
                    """ + str(student_query) + """
                    ORDER BY  sms_student.name, sms_student.father_name"""
        
        
        self.cr.execute(student_sql)
        student_rows = self.cr.fetchall()
        
        for row in student_rows:
            student_id = row[0]
            result = []
            current_class = row[3]
            class_id = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,current_class).class_id.id
            sql = """SELECT min(upper_limit) from sms_grading_scheme_line
                inner join sms_grading_scheme on 
                sms_grading_scheme.id = sms_grading_scheme_line.grading_scheme
                where class_id = """ + str(class_id)
            self.cr.execute(sql)
            lower_grade = self.cr.fetchone()[0]
            
            std_subs_sql = """SELECT sms_subject.name, sms_exam_lines.obtained_marks, sms_exam_lines.total_marks, 
                sms_academiccalendar_subjects.offered_as, sms_student_subject.id, sms_exam_lines.exam_status 
                from sms_exam_lines 
                inner join sms_student_subject 
                on 
                sms_student_subject.id = sms_exam_lines.student_subject 
                inner join sms_academiccalendar_student 
                on 
                sms_academiccalendar_student.id = sms_student_subject.student
                inner join sms_academiccalendar_subjects 
                on 
                sms_academiccalendar_subjects.id = sms_student_subject.subject
                inner join sms_subject 
                on 
                sms_subject.id = sms_academiccalendar_subjects.subject_id
                where sms_academiccalendar_student.std_id = """ + str(student_id) + """
                and sms_exam_lines.name =  """ + str(exam_type) + """
                and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                and sms_academiccalendar_subjects.reference_practical_of is null"""
            
            self.cr.execute(std_subs_sql)
            std_subs_rows = self.cr.fetchall()
            
            s_no = 1
            total_obatined_marks = 0.0;
            class_total_marks = 0.0
            count_fail = 0
            
            for std_subs_row in std_subs_rows:
                
                my_dict = {'s_no':'','title':'', 'theory':'', 'practical':'--', 'obtained_marks':0,'total_marks':'','percentage':''}
                practical_marks = 0.0
                practical_total = 0.0
                practical_rows = None
                
                if std_subs_row[3] == 'theory_practical':
                    practical_sql = """SELECT sms_subject.name, sms_exam_lines.obtained_marks, sms_exam_lines.total_marks, 
                        sms_academiccalendar_subjects.offered_as, sms_student_subject.id,sms_exam_lines.exam_status 
                        from sms_exam_lines 
                        inner join sms_student_subject 
                        on 
                        sms_student_subject.id = sms_exam_lines.student_subject 
                        inner join sms_academiccalendar_student 
                        on 
                        sms_academiccalendar_student.id = sms_student_subject.student
                        inner join sms_academiccalendar_subjects 
                        on 
                        sms_academiccalendar_subjects.id = sms_student_subject.subject
                        inner join sms_subject 
                        on 
                        sms_subject.id = sms_academiccalendar_subjects.subject_id
                        where sms_academiccalendar_student.std_id = """ + str(student_id) + """
                        and sms_exam_lines.name =  """ + str(exam_type) + """
                        and sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                        and sms_academiccalendar_subjects.reference_practical_of is not null
                        and sms_student_subject.reference_practical_of = """ + str(std_subs_row[4])
            
                    self.cr.execute(practical_sql)
                    practical_rows = self.cr.fetchone()
                    if practical_rows:
                        practical_marks = practical_rows[1]
                        practical_total = practical_rows[2]
                
                my_dict["s_no"] = s_no
                my_dict["title"] = std_subs_row[0]
                
                if std_subs_row[5] != 'Present':
                    my_dict['theory'] = std_subs_row[5]
                else:
                    my_dict["theory"] = str(round(std_subs_row[1],2))
                
                if std_subs_row[3] == 'theory_practical':
                    if practical_rows:
                        if practical_rows[5] != 'Present':
                            my_dict['practical'] = practical_rows[5]
                        else:
                            my_dict["practical"] = str(round(practical_marks,2))
                else:
                    my_dict["practical"] = practical_marks
                
                my_dict["obtained_marks"] = str(round(std_subs_row[1] + practical_marks, 2))
                my_dict["total_marks"] = round(std_subs_row[2] + practical_total, 2)
                
                if (std_subs_row[2]+practical_total) == 0:
                    obt_percentage = 0
                else:
                    obt_percentage = round(( (std_subs_row[1]+practical_marks) / (std_subs_row[2]+practical_total) ) * 100,2)
                my_dict["percentage"] = str(obt_percentage)
                
                if obt_percentage <= lower_grade:
                    count_fail = count_fail + 1  
                result.append(my_dict)
                
                total_obatined_marks = total_obatined_marks + std_subs_row[1] + practical_marks
                class_total_marks = class_total_marks + std_subs_row[2] + practical_total
                
                s_no = s_no + 1
            
            final_dict = {'result':'','total_students':'','position':'','grade':'','remarks':'','student_class_status':'','cadidate_no':'','student_name':'','father_name':'','section':'','gender':'','total_obtained_marks':'','total_obtained_percentage':'','class_total_marks':''}
            
            sql = """SELECT sms_student.registration_no, sms_student.name, 
                sms_student.father_name, sms_student.gender,current_class from sms_student
                inner join sms_academiccalendar_student on
                sms_student.id = sms_academiccalendar_student.std_id 
                WHERE sms_student.id = """ + str(student_id) + """
                AND sms_academiccalendar_student.name = """ + str(academiccalendar_id)
                    
            self.cr.execute(sql)
            row= self.cr.fetchone()
            if row:
                current_class = row[4]
                student_section = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,current_class).section_id.name
                final_dict['result'] = result
                final_dict['section'] = student_section
                final_dict['cadidate_no'] = row[0]
                final_dict['student_name'] = row[1]
                final_dict['father_name'] = row[2]
                final_dict['total_obtained_marks'] =  round(total_obatined_marks,2)
                final_dict['class_total_marks'] =  round(class_total_marks,2)
                if class_total_marks == 0:
                    percentage = 0
                else:
                    percentage = round((total_obatined_marks/class_total_marks) * 100,2)
                    
                final_dict['total_obtained_percentage'] = percentage
                
                if count_fail < 3:
                    final_dict['student_class_status'] = 'Pass'
                else:
                    final_dict['student_class_status'] = 'Fail'
                
                sql = """SELECT sms_grading_scheme_line.name, sms_grading_scheme_line.subject_remarks
                    FROM sms_grading_scheme_line 
                    inner join sms_grading_scheme on 
                    sms_grading_scheme.id = sms_grading_scheme_line.grading_scheme
                    WHERE FLOOR(""" + str(percentage) + """) between sms_grading_scheme_line.lower_limit AND sms_grading_scheme_line.upper_limit
                    AND class_id  = (SELECT class_id from sms_academiccalendar where id = """ + str(academiccalendar_id) + """)"""
                
                self.cr.execute(sql)
                grading_row = self.cr.fetchone()
        
                final_dict['grade'] = grading_row[0]
                final_dict['remarks'] = grading_row[1]
                
                sql = """SELECT count(marks) from (SELECT 
                    (SELECT sum(obtained_marks) from sms_exam_lines where student_subject in 
                    (SELECT id from sms_student_subject where  student in 
                    (SELECT id from sms_academiccalendar_student where std_id = sms_student.id))
                    and sms_exam_lines.name = """ + str(exam_type) + """) as marks
                    from sms_student 
                    inner join sms_academiccalendar_student
                    on sms_student.id = sms_academiccalendar_student.std_id
                    where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted')a
                    where marks > """ + str(total_obatined_marks)
                
                self.cr.execute(sql)
                final_dict['position'] = self.cr.fetchone()[0] + 1

                sql = """SELECT count(marks) from (SELECT 
                    (SELECT sum(obtained_marks) from sms_exam_lines where student_subject in 
                    (SELECT id from sms_student_subject where  student in 
                    (SELECT id from sms_academiccalendar_student where std_id = sms_student.id))
                    and sms_exam_lines.name = """ + str(exam_type) + """) as marks
                    from sms_student 
                    inner join sms_academiccalendar_student
                    on sms_student.id = sms_academiccalendar_student.std_id
                    where sms_academiccalendar_student.name = """ + str(academiccalendar_id) + """
                    and sms_student.state = 'Admitted')a"""
                
                self.cr.execute(sql)
                final_dict['total_students'] = self.cr.fetchone()[0]
                
                my_dict = {'s_no':'','title':'', 'theory':'', 'practical':'--', 'obtained_marks':0,'total_marks':'','percentage':''}
               
#                 my_dict = {'s_no':'Total','title':'', 'theory':'', 'practical':'', 'obtained_marks':round(total_obatined_marks,2),
#                            'total_marks':round(class_total_marks,2),'percentage':percentage}
#                 result.append(my_dict)
            

                if row[3]=='Male':
                    final_dict['gender'] = '/S/o'
                else:
                    final_dict['gender'] = '/D/o'
                
            final_result.append(final_dict)
            
        return final_result
    
       
report_sxw.report_sxw('report.sms.student.dmc_formate2.name', 'sms.student', 'addons/sms/sms_dmc_multiple_format.rml',parser = sms_dmc_multiple_format_parser, header='External')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

