from openerp.osv import fields, osv
import datetime

class admit_student(osv.osv_memory):

    def _get_student(self, cr, uid, ids):
       
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id
   
    def _get_active_session(self, cr, uid, context={}):
        ssn = self.pool.get('sms.session').search(cr, uid, [('state','=','Active')])
        if ssn:
            return ssn[0]
        else:
            return []
   
    _name = "admit.student"
    _description = "admits student in a selected class"
    _columns = {
              'student': fields.many2one('sms.student', 'Student', help="Student to be admitted", readonly = True),
              'academic_session': fields.many2one('sms.academics.session', 'Academic Session', domain="[('state','!=','Closed')]", help="Student will be admitted belongs to selected session"),
              'session': fields.many2one('sms.session', 'Session', domain="[('state','!=','Previous'),('academic_session_id','=',academic_session)]", help="Student will be admitted belongs to selected session"),
              "name": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','in',['Draft','Subjects_Loaded','Active'])]", required=True, help="1: Only Draft & Active Classes are displayed here.\n2: Class Fee must be set before getting admission in that class. "),
              'fee_update_till':fields.many2one('sms.session.months','Fee Updated Till'),
              'fee_structure': fields.many2one('sms.feestructure', 'Fee Structure',  required=True, help="Select A Fee Structure for this student."),
              'fee_starting_month': fields.many2one('sms.session.months', 'Starting Fee Month', domain="[('session_id','=',session)]", required=True, help="Select A starting month for fee of this student "),
#               'std_fees_ids': fields.one2many('sms.wiz.studentfee','parent_wiz_id','Students'),
               'helptext':fields.char(string ='Help Text',size = 400)
               }
    _defaults = {
         'student':_get_student,
           }
   
    def onchange_fee_staring_month(self, cr, uid, ids, fee_starting_month,fee_str,acad_cal, context=None):
        result = {}
        string = ''
        if not acad_cal:
            result['helptext'] = 'Select A class First' 
            result['fee_structure'] = None
            return {'value': result}
        else:
            current_month = int(datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d').strftime('%m'))
            session_id = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal).session_id.id
            current_month_in_session = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',session_id),('session_month_id','=',current_month)])[0]
            counted_month =  int(current_month_in_session) - int(fee_starting_month)
#             this_class_fees = self.pool.get('smsfee.academiccalendar.fees').search(cr, uid, [('academic_cal_id','=', acad_cal),('fee_structure_id','=', fee_str)])
            # Get this class admission fee
            
            sqlfee1 =  """SELECT smsfee_academiccalendar_fees.id
                            FROM smsfee_academiccalendar_fees
                            INNER JOIN smsfee_feetypes
                            ON smsfee_feetypes.id = smsfee_academiccalendar_fees.fee_type_id
                            WHERE smsfee_academiccalendar_fees.academic_cal_id ="""+str(acad_cal)+"""
                            AND smsfee_academiccalendar_fees.fee_structure_id="""+str(fee_str)+"""
                            AND smsfee_feetypes.subtype IN('at_admission','Monthly_Fee','Annual_fee')
                            """
            cr.execute(sqlfee1)
            this_class_fees = cr.fetchall() 
            if this_class_fees:
                total = 0
                for class_fee in this_class_fees:
                    obj = self.pool.get('smsfee.academiccalendar.fees').browse(cr,uid,class_fee[0])
                    fs = obj.fee_structure_id.name
                    ft = obj.fee_type_id.name
                   
                    total = total + int(obj.amount)
                    string += str(ft)+"="+str(obj.amount)+",\n "
                result['helptext'] = string
                return {'value': result}
            else:
                return {}
   
    def onchange_acad_cal(self, cr, uid, ids, acad_cal):
        result = {}
        acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal)
        acad_session_id = acad_cal_obj.acad_session_id.id
        result['academic_session'] = acad_session_id 
        result['fee_update_till'] = acad_cal_obj.fee_update_till.id
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
   
    def register_student(self, cr, uid, ids, data):
        result = []
        ftlist = []
        stdobj = self.pool.get('sms.student').browse(cr, uid, data['active_id'])
       
        std_id =  stdobj.id
        for f in self.browse(cr, uid, ids):
            print "acad cal,",f.name.id
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
                    
                admn_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr,uid,std_cal_id,acad_cal_obj.id,)
                self.pool.get('sms.student').write(cr, uid, data['active_id'], {'registration_no':admn_no,'fee_starting_month':f.fee_starting_month.id,'fee_type':f.fee_structure.id, 'state': 'Admitted', 'current_state': 'Current','admitted_to_class':f.name.id,'admitted_on':datetime.date.today(),'current_class':f.name.id})
                cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,f.name.id)
                #
                
#               first insert all non motnly fees(search for fee with subtype at_admission)
                sqlfee1 =  """SELECT smsfee_academiccalendar_fees.id,smsfee_feetypes.id,smsfee_feetypes.subtype
                            FROM smsfee_academiccalendar_fees
                            INNER JOIN smsfee_feetypes
                            ON smsfee_feetypes.id = smsfee_academiccalendar_fees.fee_type_id
                            WHERE smsfee_academiccalendar_fees.academic_cal_id ="""+str(f.name.id)+"""
                            AND smsfee_academiccalendar_fees.fee_structure_id="""+str(f.fee_structure.id)+"""
                            AND smsfee_feetypes.subtype IN('at_admission','Monthly_Fee','Annual_fee')
                            """
                cr.execute(sqlfee1)
                fees_ids = cr.fetchall() 
                print "this class fees,fees_ids",fees_ids   
                if fees_ids:
                    late_fee = 0
                    fee_month = ''
                    for idds in fees_ids:
                        
                        obj = self.pool.get('smsfee.academiccalendar.fees').browse(cr,uid,idds[0])
                        if idds[2] == 'Monthly_Fee':
                            print "calling method"
                            insert_monthly_fee = self.pool.get('smsfee.studentfee').insert_student_monthly_fee(cr,uid,std_id,std_cal_id,f.name.id,f.fee_starting_month.id,idds[0])
                        else:
                            print "executing else"  
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
#                 # now insert all month fee , get it from the classes with a fee structure and then insert
#                     sqlfee2 =  """SELECT smsfee_academiccalendar_fees.id from smsfee_academiccalendar_fees
#                             INNER JOIN smsfee_feetypes
#                             ON smsfee_feetypes.id = smsfee_academiccalendar_fees.fee_type_id
#                             WHERE smsfee_academiccalendar_fees.academic_cal_id ="""+str(f.name.id)+"""
#                             AND smsfee_academiccalendar_fees.fee_structure_id="""+str(f.fee_structure.id)+"""
#                             AND smsfee_feetypes.subtype ='Monthly_Fee'
#                             AND smsfee_feetypes.id IN"""+str(ftlist)+""""""
#            
#                     cr.execute(sqlfee2)
#                     fees_ids2 = cr.fetchall()
#                    
#                     #get update month of the class
#                     current_month = s_month = int(datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d').strftime('%m'))
#                     current_month_in_session = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',acad_cal_obj.session_id.id),('session_month_id','=',current_month)])[0]
#                     print "current month in session:",current_month_in_session
#                     class_fee_updated_till = acad_cal_obj.fee_update_till.id
#                     print "fee updated till:",class_fee_updated_till
#                   
#                     #Now brows its session month ids, that will be saved as fee month
#                     print "starting month:",f.fee_starting_month.id
# #                     if class_fee_updated_till > current_month_in_session:
# #                         session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',acad_cal_obj.session_id.id),('id','>=',f.fee_starting_month.id),('id','<=',class_fee_updated_till)])
# #                     else:
#                     session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',acad_cal_obj.session_id.id),('id','>=',f.fee_starting_month.id),('id','<=',class_fee_updated_till)])
#                     print "this session months:",session_months
#                     rec_months = self.pool.get('sms.session.months').browse(cr,uid,session_months)      
#                     for month1 in rec_months:
#                         late_fee = 0
#                         for fee in fees_ids2:
#                             obj3 = self.pool.get('smsfee.academiccalendar.fees').browse(cr,uid,fee[0])
#                             fee_already_exists =  self.pool.get('smsfee.studentfee').search(cr,uid,[('student_id','=',std_id),('fee_type','>=',obj3.id),('fee_month','>=',month1.id)])
#                             if fee_already_exists:
#                                 print "fee already exists"
#                             else:
#                                
#                                 create_fee2 = self.pool.get('smsfee.studentfee').create(cr,uid,{
#                                 'student_id': std_id,
#                                 'acad_cal_id': f.name.id,
#                                 'date_fee_charged': datetime.date.today(),
#                                 'acad_cal_std_id': std_cal_id,
#                                 'fee_type': obj3.id,
#                                 'generic_fee_type':obj3.fee_type_id.id,
#                                 'fee_month': month1.id,
#                                 'due_month': month1.id,
#                                 'fee_amount': obj3.amount,
#                                 'late_fee': late_fee,
#                                 'total_amount': obj3.amount + late_fee,
#                                 'reconcile':False
#                                 })
#                        
#                 else:
#                     raise osv.except_osv(('No Fee Found'),('Please Define a Fee For students promotion'))
                         
#                 else:
#                     raise osv.except_osv(_('No Fee Strucuturer found'), _('Fee Structure Not Defined for the selected Class, First Define A Fee Structure.'))
#                     raise osv.except_osv(('No Fee Strucuturer found '), ('Fee Structure Not Defined for the selected Class, First Define A Fee Structure.' ))       
        return result
admit_student()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: