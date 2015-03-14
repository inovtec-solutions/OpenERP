from openerp.osv import fields, osv
import datetime

class demote_student(osv.osv_memory):
    """Use this wizard to withdraw student from the school, cases may be student (struck_off,admission cancel,slc,deceased)"""
     
    def _get_student(self, cr, uid, ids):
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id
    
    def _get_student_class(self, cr, uid, ids):
        stdobj = self.browse(cr, uid, ids['active_id'])
        cur_class = self.pool.get('sms.academiccalendar.student').search(cr, uid, [('std_id' ,'=',stdobj.id),('state','=','Current')])
        
        if cur_class:
            cal_id = self.pool.get('sms.academiccalendar.student').browse(cr, uid, cur_class[0]).name.id
            return cal_id
        else:
            return False
    def _get_fee_month(self, cr, uid, ids):
        cur_class = self._get_student_class
        fm = self.pool.get('sms.academiccalendar.student').browse(cr, uid, cur_class).fee_update_till
        return fm
    
    _name = "demote.student"
    _description = "Demotes a student to his previous class"
    _columns = {
              'student': fields.many2one('sms.student', 'Student', help="Student to be Demoted", readonly = True),
              'current_class': fields.many2one('sms.academiccalendar','Current_class',readonly = True),
              'fee_register':fields.related('current_class','fee_update_till',type='many2one',relation='sms.session.months', string='Fee Register', readonly=True),
              'assigned_class':fields.many2one('sms.academiccalendar','New Class'),
              'reason_demote': fields.text('Reason', required = True),
             }
    _defaults = {
        'student':_get_student,
        'current_class':_get_student_class,
           }

    def demote_student(self, cr, uid, ids, data):
        result = []
        
        for f in self.browse(cr, uid, ids):
            student = f.student.id
            cur_class =  f.current_class.id
            new_class = f.assigned_class.id
            reason =  f.reason_demote
            std_acad = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('std_id','=',student),('name','=',cur_class),('state','=','Current')])[0]
            if std_acad:
# #                 Make current class of student de-active
                deactive_class = self.pool.get('sms.academiccalendar.student').write(cr,uid,std_acad,{'state': 'Demoted'})
                if deactive_class:
#                       search subjects of student and make it de-active
                    std_subs = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',std_acad),('subject_status','=','Current')])
                    for sub in std_subs:
                        add_subs = self.pool.get('sms.student.subject').write(cr,uid,sub,{'subject_status': 'Suspended'})
                    #assign new class
                    new_class_student = self.pool.get('sms.academiccalendar.student').create(cr, uid, {
                          'name': new_class,
                          'std_id':student,
                          'state': 'Current'})
                    if new_class_student:
                        self.pool.get('sms.student').write(cr,uid,student,{'current_class': new_class})
                        #assinge new subjects
                        acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',new_class),('state','!=','Complete')])
                        for sub in acad_subs:
                            add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                            'student': new_class_student,
                            'student_id': student,
                            'subject': sub,
                            'subject_status': 'Current'})
        return result
demote_student()

