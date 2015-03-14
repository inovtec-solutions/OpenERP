from openerp.osv import fields, osv

class sms_student_subject_assignment(osv.osv_memory):

    _name = "sms.student.subject.assignment"
    _description = "Subject Assignment"
    _columns = {
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True,),
                'subject_id': fields.many2one('sms.subject','Select Subject', required=True),
                'teacher_id': fields.many2one('hr.employee','Teacher', required=True),
                'offered_as': fields.selection([('theory','Theory Only'),('theory_practical','Theory + Practical'),('practical','Practical Only')], 'Offered As'),
                'academiccalendar_subject_id': fields.many2one('sms.academiccalendar.subjects','Practical of', domain="[('academic_calendar','=',academiccalendar_id)]"),
            }
    _defaults = {
            'offered_as': 'theory',
           }
    
    def onchange_academiccalendar(self, cr, uid, ids, context=None):
        result = {}
        result['academiccalendar_subject_id'] = None
        return {'value': result}

    def assign_subject(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)       
        
        for obj in current_obj:
            subject_id = None
            if obj.offered_as == 'practical':
                acad_subject_exist = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('reference_practical_of','=',None),('subject_id','=',obj.subject_id.id),('academic_calendar','=',obj.academiccalendar_id.id)])
                if acad_subject_exist:
                    subject_id = acad_subject_exist[0]
                    self.pool.get('sms.academiccalendar.subjects').write(cr, uid, subject_id, {'reference_practical_of':obj.academiccalendar_subject_id.id,'offered_as':obj.offered_as,})
                else:
                    subject_id = self.pool.get('sms.academiccalendar.subjects').create(cr,uid,{
                        'subject_id':obj.subject_id.id,                                                       
                        'academic_calendar':obj.academiccalendar_id.id,
                        'total_marks':100,
                        'passing_marks':40, 
                        'state':'Current',
                        'teacher_id':obj.teacher_id.id,
                        'offered_as':obj.offered_as,
                        'reference_practical_of':obj.academiccalendar_subject_id.id,})
                self.pool.get('sms.academiccalendar.subjects').write(cr, uid, obj.academiccalendar_subject_id.id, {'offered_as':'theory_practical',})

            else:
                acad_subject_exist = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('subject_id','=',obj.subject_id.id),('academic_calendar','=',obj.academiccalendar_id.id)])
                if acad_subject_exist:
                    subject_id = acad_subject_exist[0]
                    self.pool.get('sms.academiccalendar.subjects').write(cr, uid, subject_id, {'offered_as':obj.offered_as,})
                else:
                    subject_id = self.pool.get('sms.academiccalendar.subjects').create(cr,uid,{
                        'subject_id':obj.subject_id.id,                                                       
                        'academic_calendar':obj.academiccalendar_id.id,
                        'total_marks':100,
                        'passing_marks':40, 
                        'state':'Current',
                        'offered_as':obj.offered_as,
                        'teacher_id':obj.teacher_id.id,})
            
            student_ids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',obj.academiccalendar_id.id)])
            student_objs = self.pool.get('sms.academiccalendar.student').browse(cr, uid, student_ids, context=context)
            
            for student_obj in student_objs:
                reference_practical_of = None
                if obj.offered_as == 'practical':
                    reference_practical_of = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',student_obj.id),('subject','=',obj.academiccalendar_subject_id.id)])[0]

                student_subject_exist = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',student_obj.id),('subject','=',subject_id)])
                if student_subject_exist:
                    self.pool.get('sms.student.subject').write(cr, uid, student_subject_exist[0], {'reference_practical_of':reference_practical_of,})
                else:
                   self.pool.get('sms.student.subject').create(cr,uid,{
                        'student':student_obj.id,                                                       
                        'subject':subject_id,
                        'student_id':student_obj.std_id.id,
                        'reference_practical_of':reference_practical_of,})
        
        return {}
        
sms_student_subject_assignment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: