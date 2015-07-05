from openerp.osv import fields, osv
import datetime

class exam_entry(osv.osv_memory):

    def onchange_exam_type(self, cr, uid, ids, academiccalendar_id, context=None):
        employee_ids = []
        
        sql = """SELECT distinct uid FROM  res_groups 
            inner join res_groups_users_rel on 
            res_groups.id = res_groups_users_rel.gid
            where (res_groups.name = 'Exam Officer' or res_groups.name = 'Exam Manager') 
            AND res_groups_users_rel.uid = """ + str(uid)
        cr.execute(sql)
        if cr.fetchone():
            employee_ids = self.pool.get('hr.employee').search(cr,uid,[])
        else:
            resource_ids = self.pool.get('resource.resource').search(cr,uid,[('user_id','=',uid)])
            employee_ids = self.pool.get('hr.employee').search(cr,uid,[('resource_id','in',resource_ids)])
        
        print {'subject_id':[('academic_calendar','=',academiccalendar_id),('teacher_id','in',employee_ids)]}
        return {'domain':{'subject_id':[('academic_calendar','=',academiccalendar_id),('teacher_id','in',employee_ids)]}}

    _name = "exam.entry"
    _description = "Timetable Entry"
    _columns = {
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True),
                'exam_type': fields.many2one('sms.exam.datesheet','Exam Type', required=True, domain="[('academiccalendar','=',academiccalendar_id),('status','=','Active')]"),
                'subject_id': fields.many2one('sms.academiccalendar.subjects','Subject', domain="[('academic_calendar','=',academiccalendar_id)]", required=True),
              }
    _defaults = {
           }
    
    def onchange_academiccalendar(self, cr, uid, ids, context=None):
        result = {}
        result['subject_id'] = None
        result['exam_type'] = None
        return {'value': result}

    def exam_entry(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        
        cr.execute("""select id,name from ir_ui_view 
                    where model= 'sms.exam.default.lines' 
                    and type='tree'""")
        view_res = cr.fetchone()
            
        sql = """SELECT * FROM(
                (SELECT sms_student.name, sms_student.father_name, sms_student.registration_no, 
                sms_student_subject.id, sms_student_subject.subject_status, sms_exam_datesheet.id as sms_exam_datesheet_id,
                sms_exam_lines.id as sms_exam_lines_id, sms_exam_lines.exam_status, sms_exam_lines.obtained_marks, sms_exam_lines.total_marks
                from sms_student 
                inner join sms_academiccalendar_student
                on sms_student.id = sms_academiccalendar_student.std_id
                inner join sms_student_subject
                on
                sms_academiccalendar_student.id = sms_student_subject.student 
                inner join sms_exam_lines
                on
                sms_student_subject.id = sms_exam_lines.student_subject 
                inner join sms_exam_datesheet
                on 
                sms_exam_lines.name = sms_exam_datesheet.id
                where sms_student_subject.subject = """ + str(current_obj[0].subject_id.id) + """ 
                and sms_academiccalendar_student.name = """ + str(current_obj[0].academiccalendar_id.id) + """
                and sms_student_subject.subject_status = 'Current'
                and sms_academiccalendar_student.state = 'Current'
                and sms_exam_datesheet.id = """ + str(current_obj[0].exam_type.id) + """
                and sms_student.state = 'Admitted')

                UNION
                (SELECT sms_student.name, sms_student.father_name, sms_student.registration_no, 
                sms_student_subject.id, sms_student_subject.subject_status, NULL AS sms_exam_datesheet_id,
                NULL AS sms_exam_lines_id, 'Present' AS sms_exam_lines_exam_status, NULL AS sms_exam_lines_obtained_marks, NULL AS sms_exam_lines_total_marks
                from sms_student 
                inner join sms_academiccalendar_student
                on sms_student.id = sms_academiccalendar_student.std_id
                inner join sms_student_subject
                on
                sms_academiccalendar_student.id = sms_student_subject.student 
                where sms_student_subject.subject = """ + str(current_obj[0].subject_id.id) + """ 
                and sms_academiccalendar_student.name = """ + str(current_obj[0].academiccalendar_id.id) + """
                and sms_student_subject.subject_status='Current'
                and sms_student.state = 'Admitted'
                and sms_academiccalendar_student.state = 'Current'
                and sms_student.id not in  (SELECT sms_student.id from sms_student 
                inner join sms_academiccalendar_student
                on sms_student.id = sms_academiccalendar_student.std_id
                inner join sms_student_subject
                on
                sms_academiccalendar_student.id = sms_student_subject.student 
                inner join sms_exam_lines
                on
                sms_student_subject.id = sms_exam_lines.student_subject 
                inner join sms_exam_datesheet
                on 
                sms_exam_lines.name = sms_exam_datesheet.id
                where sms_student_subject.subject = """ + str(current_obj[0].subject_id.id) + """ 
                and sms_academiccalendar_student.name = """ + str(current_obj[0].academiccalendar_id.id) + """
                and sms_student_subject.subject_status='Current'
                and sms_academiccalendar_student.state = 'Current'
                and sms_exam_datesheet.id = """ + str(current_obj[0].exam_type.id) + """
                and sms_student.state = 'Admitted')
                )
                )a ORDER BY subject_status, name, father_name"""
        
        cr.execute(sql)
        rec = cr.fetchall()
        
        exam_parent = self.pool.get('sms.exam')
        exam_detail = self.pool.get('sms.exam.lines')
        
        temp_parent = self.pool.get('sms.exam.default')
        temp_detail = self.pool.get('sms.exam.default.lines')
        
        lines_ids = self.pool.get('sms.exam.datesheet.lines').search(cr,uid,[('name','=',current_obj[0].exam_type.id),('subject','=',current_obj[0].subject_id.id)])
        lines_obj = self.pool.get('sms.exam.datesheet.lines').browse(cr, uid, lines_ids[0], context=context)
        
        record_exist_temp = temp_parent.search(cr,uid,[('user_id','=',uid),('subject_id','=',current_obj[0].subject_id.id)])
        sms_temp_new_id = 0
        today = datetime.date.today()
        
        if record_exist_temp:
            sql="""
            delete from sms_exam_default_lines where
            parent_default_exam = """ + str(record_exist_temp[0])
            cr.execute(sql)
            cr.commit()
            
            sql="""
            delete from sms_exam_default where
            id = """ + str(record_exist_temp[0])
            cr.execute(sql)
            cr.commit()
            
            sms_temp_new_id = temp_parent.create(cr,uid,{'user_id':uid, 'entry_date':today, 'subject_id':current_obj[0].subject_id.id})
        else:
            sms_temp_new_id = temp_parent.create(cr,uid,{'user_id':uid, 'entry_date':today, 'subject_id':current_obj[0].subject_id.id})
    
        exam_record_exist = exam_parent.search(cr,uid,[('subject_id','=',current_obj[0].subject_id.id),('name','=',current_obj[0].exam_type.id)])
        if exam_record_exist:
            exam_new_id = exam_record_exist[0]
        else: 
            exam_new_id = exam_parent.create(cr,uid,{'entry_date':today, 'subject_id':current_obj[0].subject_id.id, 'name':current_obj[0].exam_type.id})
        
        for each in rec:
            exam_id = each[6]
            if each[6]:
                sms_temp_detail_new_id = temp_detail.create(cr,uid,
                {
                'name':each[0],
                'father_name':each[1],
                'registration_no':each[2],
                'student_subject':each[3],
                'student_subject_status':each[4],
                'exam_type':each[5],
                'exam_id':exam_id,
                'exam_status':each[7],
                'obtained_marks':each[8],
                'total_marks':lines_obj.total_marks,
                'parent_default_exam':sms_temp_new_id,
                })
                exam_detail.write(cr, uid, [each[6]], {'total_marks':lines_obj.total_marks})
                
            else:
                exam_detail_new_id = exam_detail.create(cr,uid,
                {
                'student_subject':each[3],
                'student_subject_status':each[4],
                'name':current_obj[0].exam_type.id,
                'exam_status':each[7],
                'obtained_marks':0,
                'total_marks':lines_obj.total_marks,
                'parent_exam':exam_new_id,
                })
                
                sms_temp_detail_new_id = temp_detail.create(cr,uid,
                {
                'name':each[0],
                'father_name':each[1],
                'registration_no':each[2],
                'student_subject':each[3],
                'student_subject_status':each[4],
                'exam_type':current_obj[0].exam_type.id,
                'exam_id':exam_detail_new_id,
                'exam_status':each[7],
                'obtained_marks':0,
                'total_marks':lines_obj.total_marks,
                'parent_default_exam':sms_temp_new_id,
                })
                
        return {
            'domain': "[('parent_default_exam','=',"+str(sms_temp_new_id)+")]",
            'name': 'Exam Entry for ' +  str(current_obj[0].exam_type.name) + "  " + str(current_obj[0].subject_id.name),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'sms.exam.default.lines',
            'view_id': view_res,
            'type': 'ir.actions.act_window'}
        
exam_entry()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: