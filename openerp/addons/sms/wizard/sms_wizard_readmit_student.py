from openerp.osv import fields, osv
import datetime

class readmit_student(osv.osv_memory):

    def _get_student(self, cr, uid, ids):
       
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id
    
    def _get_student_class(self, cr, uid, ids):
 
         stdobj = self.browse(cr, uid, ids['active_id'])
         cur_class = self.pool.get('sms.academiccalendar.student').search(cr, uid, [('std_id' ,'=',stdobj.id),('state','=','Suspended')])
         
         if cur_class:
             cal_id = self.pool.get('sms.academiccalendar.student').browse(cr, uid, cur_class[0]).name.id
             return cal_id
         else:
             return False

#     def _get_student_class(self, cr, uid, ids, name, arg=None, context={}):
#         result = {}
#         records = self.browse(cr, uid, ids, context)
#         for f in records:
#             if f.entry_type == 'Student':
#                 result[f.id] = self.pool.get('sms.student').browse(cr,uid,f.student.id).current_class.id
#             else:
#                 result[f.id] = "Employee"
#         return result

    
    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
        else:
            return []
   
    _name = "readmit.student"
    _description = "Re-admits student in a selected class"
    _columns = {
              'student': fields.many2one('sms.student', 'Student', help="Student to be admitted", readonly = True),
              'academic_session': fields.many2one('sms.academics.session', 'Academic Session', domain="[('state','!=','Closed')]", help="Student will be admitted belongs to selected session"),
              'session': fields.many2one('sms.session', 'Session', domain="[('state','!=','Previous'),('academic_session_id','=',academic_session)]", help="Student will be admitted belongs to selected session"),
              'name': fields.many2one('sms.academiccalendar', 'Student Class', help="Student class to be re-admitted in"),
              'fee_structure': fields.many2one('sms.feestructure', 'Fee Structure',  required=True, help="Select A Fee Structure for this student."),
              'fee_starting_month': fields.many2one('sms.session.months', 'Starting Fee Month', required=True, help="Select A starting month for fee of this student "),
              'helptext':fields.char(string ='Help Text',size = 400)
               }
    _defaults = {
         'student':_get_student,
         'name':_get_student_class,
           }
   
    def onchange_fee_staring_month(self, cr, uid, ids, fee_starting_month,fee_str,acad_cal, context=None):
        result = {}
        string = ''
        current_month = int(datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d').strftime('%m'))
        session_id = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal).session_id.id
        current_month_in_session = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',session_id),('session_month_id','=',current_month)])[0]
        counted_month =  int(current_month_in_session) - int(fee_starting_month)
        this_class_fees = self.pool.get('smsfee.classes.fees').search(cr, uid, [('academic_cal_id','=', acad_cal),('fee_structure_id','=', fee_str)])
        if this_class_fees:
            total = 0
            for class_fee in this_class_fees:
                obj = self.pool.get('smsfee.classes.fees').browse(cr,uid,class_fee)
                fs = obj.fee_structure_id.name
                ft = obj.fee_type_id.name
               
                total = total + int(obj.amount)
                string += str(ft)+"="+str(obj.amount)+", "
            result['helptext'] = string
            return {'value': result}
        else:
            return {}
   
    def onchange_acad_cal(self, cr, uid, ids, acad_cal):
        result = {}
        acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal)
        acad_session_id = acad_cal_obj.acad_session_id.id
        result['academic_session'] = acad_session_id
        return {'value': result}
   
   
    def onchange_academic_session(self, cr, uid, ids, ac_session, context=None):
        result = {}
        session_id = self.pool.get('sms.session').search(cr, uid, [('academic_session_id','=', ac_session),('state','=', 'Active')])
        if session_id:
            result['session'] = session_id[0]
            return {'value': result}
        else:
            return {}
   
    def register_student(self, cr, uid, ids, data):
        result = []
        ftlist = []
        stdobj = self.pool.get('sms.student').browse(cr, uid, data['active_id'])
       
        std_id =  stdobj.id
        acad_cal_std_id = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('std_id','=',std_id)])
        acad_cal_std_obj = self.pool.get('sms.academiccalendar.student').browse(cr,uid,acad_cal_std_id[0])
        for f in self.browse(cr, uid, ids):
            acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,f.name.id)
            updated_month = self.pool.get('smsfee.classfees.register').search(cr,uid,[('academic_cal_id','=',f.name.id)])
            std_cal_id = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                 'name':f.name.id,
                 'date_enrolled':datetime.date.today(),
                 'enrolled_by':uid,                                              
                 'std_id':std_id,
                 'date_registered':datetime.date.today(),
                 'state':'Current' })
            if std_cal_id:
                 # Add subjects to student
                 acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',f.name.id),('state','!=','Complete')])
                 for sub in acad_subs:
                     add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                     'student': std_cal_id,
                     'student_id': std_id,
                     'subject': sub,
                     'subject_status': 'Current'})
                    
#                 admn_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr,uid,std_cal_id,acad_cal_obj.id,)
            self.pool.get('sms.student').write(cr, uid, data['active_id'], {'fee_starting_month':f.fee_starting_month.id,'fee_type':f.fee_structure.id, 'state': 'Admitted', 'current_state': 'Current','admitted_to_class':f.name.id,'admitted_on':datetime.date.today(),'current_class':f.name.id})
            cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,f.name.id)
            # Now insert all fees athat are applied on re-adminssion
            sqlfee1 =  """SELECT smsfee_classes_fees.id,smsfee_feetypes.id,smsfee_feetypes.subtype
                            FROM smsfee_classes_fees
                            INNER JOIN smsfee_feetypes
                            ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                            WHERE smsfee_classes_fees.academic_cal_id ="""+str(f.name.id)+"""
                            AND smsfee_classes_fees.fee_structure_id="""+str(f.fee_structure.id)+"""
                            AND smsfee_feetypes.subtype IN('at_admission','Monthly_Fee','Annual_fee')
                            """
            cr.execute(sqlfee1)
            fees_ids = cr.fetchall() 
            if fees_ids:
                late_fee = 0
                fee_month = ''
                for idds in fees_ids:
                    
                    obj = self.pool.get('smsfee.classes.fees').browse(cr,uid,idds[0])
                    if idds[2] == 'Monthly_Fee':
                        insert_monthly_fee = self.pool.get('smsfee.studentfee').insert_student_monthly_fee(cr,uid,std_id,std_cal_id,f.name.id,f.fee_starting_month.id,idds[0])
                    else:
                        crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                        'student_id': std_id,
                        'acad_cal_id': f.name.id,
                        'acad_cal_std_id': std_cal_id,
                        'fee_type': obj.id,
                        'generic_fee_type':idds[1],
                        'date_fee_charged':datetime.date.today(),
                        'due_month': f.fee_starting_month.id,
                        'fee_amount': obj.amount,
                        'paid_amount':0,
                        'late_fee':0,
                        'total_amount':obj.amount + late_fee,
                        'reconcile':False,
                        'state':'fee_unpaid'
                        })
                else:
                      msg = 'Fee May be defined but not set for New Class:'                     
#                 else:
#                     raise osv.except_osv(_('No Fee Strucuturer found'), _('Fee Structure Not Defined for the selected Class, First Define A Fee Structure.'))
#                     raise osv.except_osv(('No Fee Strucuturer found '), ('Fee Structure Not Defined for the selected Class, First Define A Fee Structure.' ))       
        return result
readmit_student()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: