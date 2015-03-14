from openerp.osv import fields, osv
import datetime

class change_student_class(osv.osv_memory):

    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        return ssn[0]
    
    _name = "change.student.class"
    _description = "Student Change Section"
    _columns = {
                'student_class': fields.many2one('sms.academiccalendar','From Class', domain="[('state','!=','Complete')]", required=True),
                'student_id': fields.many2one('sms.student','Student', domain="[('current_class','=',student_class),('state','=','Admitted')]", required=True),
                'new_class_id': fields.many2one('sms.academiccalendar','To Class', domain="[('state','!=','Complete'),('id','!=',student_class)]", required=True),
                'academic_session': fields.many2one('sms.academics.session', 'Academic Session', domain="[('state','!=','Closed')]", help="Student will be admitted belongs to selected session"),
                'session': fields.many2one('sms.session', 'Session', domain="[('state','!=','Previous'),('academic_session_id','=',academic_session)]", help="Student will be admitted belongs to selected session"),
                'fee_structure': fields.many2one('sms.feestructure', 'Fee Structure',  required=True, help="Select A Fee Structure for this student."),
                'fee_starting_month': fields.many2one('sms.session.months', 'Starting Fee Month', domain="[('session_id','=',session)]", required=True, help="Select A starting month for fee of this student "),
                
              }
    _defaults = {
                 }
    
    def onchange_acad_cal(self, cr, uid, ids, acad_cal):
        result = {}
        acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal)
        acad_session_id = acad_cal_obj.acad_session_id.id
        print "acad_session_id:",acad_session_id
        result['academic_session'] = acad_session_id
        return {'value': result}       
    
    def onchange_academic_session(self, cr, uid, ids, ac_session, context=None):
        result = {}
        session_id = self.pool.get('sms.session').search(cr, uid, [('academic_session_id','=', ac_session),('state','=', 'Active')])
        if session_id:
            print "session found:",session_id
            result['session'] = session_id[0]
            return {'value': result}
        else:
            return {} 
    
    def change_student_class(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        for f in self.browse(cr, uid, ids, context=context):
        
            #First check if fm is enabled update relvent journals
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            if user.company_id.enable_fm:
                journals_updated = self.pool.get('sms.student.promotion').change_student_class_Journal_enteries(self, cr, uid, f.student_id.id,f.student_class.id)
            #2: Delete student fee ad classes
            print "111111111", f.student_id.id
            print "111111112", f.student_class.id
            print "111111113", f.new_class_id
            print "111111114", f.fee_structure
            print "111111115",  f.fee_starting_month
            fee_class_deleted = self.pool.get('sms.academiccalendar').change_student_class(self, cr, uid, f.student_id.id,f.student_class.id,f.new_class_id,f.fee_structure,f.fee_starting_month)
        
                
change_student_class()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: