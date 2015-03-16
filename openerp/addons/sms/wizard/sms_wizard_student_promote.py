
from openerp.osv import fields, osv
import datetime

class student_promote(osv.osv_memory):

    _name = "student.promote"
    _description = "Student Promotion"
    _columns = {
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Promote from Class', domain="[('state','not in',['Draft','Complete'])]", required=True),
                'exam_type': fields.many2one('sms.exam.datesheet','Exam To Show', required=True, domain="[('academiccalendar','=',academiccalendar_id)]"),
                'academiccalendar_to_id': fields.many2one('sms.academiccalendar','Promoted to Class', required=True),
              }
    _defaults = {
           }
    
    def onchange_academiccalendar(self, cr, uid, ids, academiccalendar_id, context=None):
        result = {}
        current_obj = self.pool.get('sms.academiccalendar').browse(cr, uid, academiccalendar_id, context=context)
        sequence = current_obj.class_id.sequence
        class_id = self.pool.get('sms.classes').search(cr,uid,[('sequence','=',sequence+1)])
        academiccalendar_ids = self.pool.get('sms.academiccalendar').search(cr,uid,[('class_id','=',class_id),('state','in',['Draft','Active']),('session_id','!=',current_obj.session_id.id)])
        res = {'domain': {'academiccalendar_to_id': [('id', 'in', academiccalendar_ids)]}}
        return res 
        
    def student_promote(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        
        cr.execute("""select id,name from ir_ui_view 
                    where model= 'sms.student.promotion' 
                    and type='tree'""")
        view_res = cr.fetchone()
            
        sql="""delete from sms_student_promotion"""
        cr.execute(sql)
        cr.commit()

        sql = """SELECT sms_student.id, sms_student.registration_no, sms_student.name, sms_student.father_name, sms_academiccalendar_student.id
            from sms_student 
            inner join sms_academiccalendar_student
            on sms_student.id = sms_academiccalendar_student.std_id
            where sms_academiccalendar_student.name = """ + str(current_obj[0].academiccalendar_id.id) + """
            and sms_academiccalendar_student.state = 'Current'
            and sms_student.state = 'Admitted'
            ORDER BY name, father_name"""
        
        cr.execute(sql)
        student_rows = cr.fetchall()
        
        for student_row in student_rows:
            sql = """SELECT sum(sms_exam_lines.obtained_marks), sum(sms_exam_lines.total_marks)
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
                    where sms_academiccalendar_student.name = """ + str(current_obj[0].academiccalendar_id.id) + """
                    and sms_exam_datesheet.id = """ + str(current_obj[0].exam_type.id) + """
                    and sms_student.id = """ + str(student_row[0])
            
            cr.execute(sql)
            marks_row = cr.fetchone()        
           
            sms_temp_detail_new_id = self.pool.get('sms.student.promotion').create(cr,uid,
            {
                'student':student_row[0],
                'registration_no':student_row[1],
                'name':student_row[2],
                'father_name':student_row[3],
                'sms_academiccalendar_student':student_row[4],
                'sms_academiccalendar_from':current_obj[0].academiccalendar_id.id,
                'sms_academiccalendar_to':current_obj[0].academiccalendar_to_id.id,
                'obtained_marks':marks_row[0],
                'total_marks':marks_row[1],
                'promote':False,
                'promote_conditionally':False,
                'discontinue':False,
                'failed':False,
                'pending':True,})
                 
        return {
            #'domain': "[('parent_default_exam','=',"+str(sms_temp_new_id)+")]",
            'name': 'Student Promotion of (' +  str(current_obj[0].academiccalendar_id.name),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'sms.student.promotion',
            'view_id': view_res,
            'type': 'ir.actions.act_window'}
        
student_promote()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: