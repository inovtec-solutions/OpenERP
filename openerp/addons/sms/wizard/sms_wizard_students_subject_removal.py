from openerp.osv import fields, osv

class sms_student_subject_removal(osv.osv_memory):

    _name = "sms.student.subject.removal"
    _description = "Subject Removal"
    _columns = {
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True,),
                'academiccalendar_subject_id': fields.many2one('sms.academiccalendar.subjects','Subject', domain="[('academic_calendar','=',academiccalendar_id)]"),
                'delete_exams': fields.boolean('Delete Exams'),
            }
    _defaults = {
            'delete_exams': False,
           }
    
    def onchange_academiccalendar(self, cr, uid, ids, context=None):
        result = {}
        result['academiccalendar_subject_id'] = None
        return {'value': result}

    def remove_subject(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)       
        
        for obj in current_obj:
            student_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',obj.academiccalendar_id.id)])
            student_objs = self.pool.get('sms.academiccalendar.student').browse(cr, uid, student_ids, context=context)
            
            exam_datesheet_lines_ids = self.pool.get('sms.exam.datesheet.lines').search(cr,uid,[('subject','=',obj.academiccalendar_subject_id.id)])
            exam_ids = self.pool.get('sms.exam').search(cr,uid,[('subject_id','=',obj.academiccalendar_subject_id.id)])
            exam_default_ids = self.pool.get('sms.exam.default').search(cr,uid,[('subject_id','=',obj.academiccalendar_subject_id.id)])
            exam_default_lines_ids = self.pool.get('sms.exam.default.lines').search(cr,uid,[('parent_default_exam','in',exam_default_ids)])
                    
            for student_obj in student_objs:
                if obj.delete_exams:
                    student_subject_ids = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',student_obj.id),('subject','=',obj.academiccalendar_subject_id.id)])
                    exam_lines_ids = self.pool.get('sms.exam.lines').search(cr,uid,[('student_subject','in',student_subject_ids)])
                    self.pool.get('sms.exam.lines').unlink(cr, uid, exam_lines_ids, context=context)
                    self.pool.get('sms.student.subject').unlink(cr, uid, student_subject_ids, context=context)
                else:
                    student_subject_ids = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',student_obj.id),('subject','=',obj.academiccalendar_subject_id.id)])
                    self.pool.get('sms.student.subject').unlink(cr, uid, student_subject_ids, context=context)
            
            if obj.delete_exams:
                self.pool.get('sms.exam.datesheet.lines').unlink(cr, uid, exam_datesheet_lines_ids, context=context)
                self.pool.get('sms.exam.default.lines').unlink(cr, uid, exam_default_lines_ids, context=context)
                self.pool.get('sms.exam.default').unlink(cr, uid, exam_default_ids, context=context)
                self.pool.get('sms.exam').unlink(cr, uid, exam_ids, context=context)
                 
            self.pool.get('sms.academiccalendar.subjects').write(cr, uid, obj.academiccalendar_subject_id.id, {'state':'Draft'})
            self.pool.get('sms.academiccalendar.subjects').unlink(cr, uid, [obj.academiccalendar_subject_id.id], context=context)
                                
        return {}
        
sms_student_subject_removal()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: