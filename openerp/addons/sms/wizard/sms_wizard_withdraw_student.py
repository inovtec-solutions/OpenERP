from openerp.osv import fields, osv
import datetime

class withdraw_student(osv.osv_memory):
    """Use this wizard to withdraw student from the school, cases may be student (struck_off,admission cancel,slc,deceased)"""
     
    def _get_student(self, cr, uid, ids):
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id
    
    _name = "withdraw.student"
    _description = "withdraws student from the school"
    _columns = {
              'student': fields.many2one('sms.student', 'Student', help="Student to be Withdrawlled", readonly = True),
              'withdraw_type': fields.selection([('admission_cancel','Admission Cancel'),('drop_out','Drop Out'),('slc','School leaving Certificate')],'Withdraw Type', required = True),
              'reason_withdraw': fields.text('Reason', required = True),
              'helptext':fields.text('Help Text')
             }
    _defaults = {
        'student':_get_student,
        'helptext':'Use Withdraw Wizard to DropOut,Cancel Admission, Issue School leaving certificate. If a wokflow is defined this wizard can work through a predefined workflow.'
           }

    def withdraw_student(self, cr, uid, ids, data):
        result = []
        
        stdobj = self.pool.get('sms.student').browse(cr, uid, data['active_id'] )
        acad_cal_id = stdobj.current_class.id
        print "acad cal id:",acad_cal_id
        cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal_id)
        std_id =  stdobj.id
        
        for f in self.browse(cr, uid, ids):
            withdrawtype =  f.withdraw_type
            reason =  f.reason_withdraw
            write = self.pool.get('sms.student').write(cr,uid,[std_id],{
                'state':withdrawtype,                                                       
                'reason_withdraw':reason,
                'date_withdraw':datetime.date.today(), 
                 })
            if write:
#               Update Class Current Strength (deduct by 1) 
                cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal_id)
#                 cur_strength = cal_obj.cur_strength
#                 print "current str ",cur_strength
#                 cur_strength = cur_strength - 1
#                 update_acad_cal = self.pool.get('sms.academiccalendar').write(cr, uid, acad_cal_id, {'cur_strength':cur_strength})
#                 ###################
                std_acad = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('std_id','=',std_id),('state','=','Current')])[0]
# #               Make current class of student de-active
                deactive_class = self.pool.get('sms.academiccalendar.student').write(cr,uid,std_acad,{'state': 'Suspended'})
#               search subjects of student and make it de-active
                std_subs = self.pool.get('sms.student.subject').search(cr,uid,[('student','=',std_acad),('subject_status','=','Current')])
                for sub in std_subs:
                    add_subs = self.pool.get('sms.student.subject').write(cr,uid,sub,{'subject_status': 'Suspended'})
        return result
withdraw_student()

