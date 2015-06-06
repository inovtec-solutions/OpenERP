from openerp.osv import fields, osv
import datetime

class assign_class_to_student(osv.osv_memory):

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
    
    _name = "assign.class.to.student"
    _description = "Assign class to failed student"
    _columns = {
              'student': fields.many2one('sms.student', 'Student', help="Student to be admitted", readonly = True),
              'session': fields.many2one('sms.session', 'Fee Structure', domain="[('state','!=','Previous')]", required=True, help="Student will be admitted belongs to selected session"),
              'name': fields.many2one('sms.academiccalendar', 'Class', domain="[('state','in',['Subjects_Loaded','Active']),('session_id','=',session)]", required=True, help="1: Only Draft & Active Classes are displayed here.\n2: Class Fee must be set before getting admission in that class. "),
              'fee_structure': fields.many2one('sms.feestructure', 'Fee Structure',  required=True, help="Select A Fee Structure for this student."),
              'fee_starting_month': fields.many2one('sms.session.months', 'Starting Fee Month', domain="[('session_id','=',session)]", required=True, help="Select A starting month for fee of this student "),
              'fee_class': fields.many2many('smsfee.academiccalendar.fees', 'failed_student_smsfee_academiccalendar_fees_rel', 'failed_student_id', 'fee_class_id','Get Fee', domain="[('academic_cal_id','=',name), ('fee_structure_id','=',fee_structure)]", required=True,),
              
#               'std_fees_ids': fields.one2many('sms.wiz.studentfee','parent_wiz_id','Students'),
               'helptext':fields.text('Help Text')
               }
    _defaults = {
         'student':_get_student,
         'session':_get_active_session,
         'helptext':'\n\nAdmit NEW Student:\n New Admissions made in the classes with Fee Structure defined and Subjects loaded.'
           }
    
    def onchange_feetype(self, cr, uid, ids, exam_status, context={}):
        sql = """SELECT admission_fee,annual_fee """
        return 
    
    def assign_class_to_student(self, cr, uid, ids, data):
        result = []
        ftlist = []
        stdobj = self.pool.get('sms.student').browse(cr, uid, data['active_id'])
        
        std_id =  stdobj.id
        for f in self.browse(cr, uid, ids):
            acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,f.name.id)
            updated_month = self.pool.get('smsfee.classfees.register').search(cr,uid,[('academic_cal_id','=',f.name.id)])
            crt = self.pool.get('sms.academiccalendar.student').create(cr,uid,{
                'name':f.name.id,                                                       
                'std_id':std_id,
                'date_registered':datetime.date.today(), 
                'state':'Current' })
            if crt:
                # Add subjects to student
                acad_subs = self.pool.get('sms.academiccalendar.subjects').search(cr,uid,[('academic_calendar','=',f.name.id),('state','!=','Complete')])
                for sub in acad_subs:
                    add_subs = self.pool.get('sms.student.subject').create(cr,uid,{
                    'student': crt,
                    'student_id': std_id,
                    'subject': sub,
                    'subject_status': 'Current'})
                     
                # i think this will not work if student failed class and new class categories are the same, there shoiuld be a chekc if failed and new class category are the same, no need to assieng new admin no
                admn_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr,uid,crt)
                self.pool.get('sms.student').write(cr, uid, data['active_id'], {'registration_no':admn_no,'fee_type':f.fee_structure.id, 'state': 'Admitted', 'current_state': 'Current','admitted_to_class':f.name.id,'admitted_on':datetime.date.today(),'current_class':f.name.id})
                #Update Class Strength
#                 cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,f.name.id)
#                 cur_strength = cal_obj.cur_strength
#                 cur_strength = cur_strength + 1
#                 update_acad_cal = self.pool.get('sms.academiccalendar').write(cr, uid, f.name.id, {'cur_strength':cur_strength})
                 #get all feetype ids from fee typs with fee type 'at_atmission'
                sql_ft = """SELECT id from smsfee_feetypes WHERE subtype IN('at_admission','Monthly_Fee','Annual_fee')"""
                cr.execute(sql_ft)
                ft_ids = cr.fetchall() 
                for ft in ft_ids:
                    ftlist.append(ft[0])
                ftlist = tuple(ftlist)
                ftlist = str(ftlist).rstrip(',)')
                ftlist = ftlist+')'
#               first insert all non motnly fees(search for fee with subtype at_admission) 
                
                fee_array = []
                for fee in f.fee_class:
                    fee_array.append(fee.id)
                
                fee_array = tuple(fee_array)
                fee_array = str(fee_array).rstrip(',)')
                fee_array = fee_array+')'
                
                if ft_ids:
                    sqlfee1 =  """SELECT smsfee_academiccalendar_fees.id from smsfee_academiccalendar_fees
                        INNER JOIN smsfee_feetypes
                        ON smsfee_feetypes.id = smsfee_academiccalendar_fees.fee_type_id
                        WHERE smsfee_feetypes.subtype <>'Monthly_Fee'
                        AND smsfee_academiccalendar_fees.id in """+str(fee_array)
                                
                                
                                        
                    cr.execute(sqlfee1)
                    fees_ids = cr.fetchall()  
                    
                            
                    if fees_ids: 
                        for idds in fees_ids:
                            obj = self.pool.get('smsfee.academiccalendar.fees').browse(cr,uid,idds[0])
                            crate_fee = self.pool.get('smsfee.studentfee').create(cr,uid,{
                            'student_id': std_id,
                            'acad_cal_id': f.name.id,
                            'acad_cal_std_id': crt,
                            'fee_type': obj.id,
                            'fee_amount': obj.amount,
                            'due_month':  acad_cal_obj.fee_update_till.id,
                            'paid_amount':0,
                            'state':'fee_unpaid',
                            })
                    else:
                          msg = 'Fee May be defined but not set for New Class:'        
#                 # now insert all month fee , get it from the classes with a fee structure and then insert
                    sqlfee2 =  """SELECT smsfee_academiccalendar_fees.id from smsfee_academiccalendar_fees
                            INNER JOIN smsfee_feetypes
                            ON smsfee_feetypes.id = smsfee_academiccalendar_fees.fee_type_id
                            WHERE smsfee_academiccalendar_fees.academic_cal_id ="""+str(f.name.id)+"""
                            AND smsfee_academiccalendar_fees.fee_structure_id="""+str(f.fee_structure.id)+"""
                            AND smsfee_feetypes.subtype ='Monthly_Fee'
                            AND smsfee_feetypes.id IN"""+str(ftlist)+""""""
            
                    cr.execute(sqlfee2)
                    fees_ids2 = cr.fetchall() 
                    
                    #get update month of the class
                    updated_month = acad_cal_obj.fee_update_till.id
                    #Now brows its session month ids, that will be saved as fee month 
                    session_months = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',acad_cal_obj.session_id.id),('id','>=',f.fee_starting_month.id)]) 
                    rec_months = self.pool.get('sms.session.months').browse(cr,uid,session_months)       
                    for month1 in rec_months:
                        if month1.id <= updated_month:
                           
                            for fee in fees_ids2:
                                obj3 = self.pool.get('smsfee.academiccalendar.fees').browse(cr,uid,fee[0])
                                create_fee2 = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                'student_id': std_id,
                                'acad_cal_id': f.name.id,
                                'date_fee_charged': datetime.date.today(),
                                'acad_cal_std_id': crt,
                                'fee_type': obj3.id,
                                'fee_month': month1.id,
                                'due_month': month1.id, 
                                'fee_amount': obj3.amount,
                                 'state':'fee_unpaid',
                                })
                            
                else:
                    raise osv.except_osv(('No Fee Found'),('Please Define a Fee For students promotion'))
                
                ###################################################################3
                #student.current_class.class_id.category
                std_class = self.pool.get('sms.academiccalendar.student').search(cr, uid,[('std_id', '=', std_id),('state', '=', 'Current')])
                
                if not std_class:
                    continue
                acad_std = self.pool.get('sms.academiccalendar.student').browse(cr, uid,std_class[0])
                category2 = acad_std.name.class_id.category
                                
                std_reg_type_exist = self.pool.get('sms.registration.nos').search(cr, uid,[('student_id', '=', std_id),('class_category', '=', category2)])

                if not std_reg_type_exist:
                    std_reg_nos = self.pool.get('sms.registration.nos').search(cr, uid,[('student_id', '=', std_id)])
                    self.pool.get('sms.registration.nos').write(cr, uid, std_reg_nos, {'is_active':False,})
                    admn_no = self.pool.get('sms.academiccalendar.student')._set_admission_no(cr,uid,std_class[0])

                    self.pool.get('sms.registration.nos').create(cr, uid, {
                        'student_id': std_id,
                        'name': admn_no,
                        'class_category': category2,
                        'is_active': True,})
                    self.pool.get('sms.student').write(cr, uid, std_id, {'registration_no':admn_no,})
                ###################################################################3
          
#                 else:
#                     raise osv.except_osv(_('No Fee Strucuturer found'), _('Fee Structure Not Defined for the selected Class, First Define A Fee Structure.'))
#                     raise osv.except_osv(('No Fee Strucuturer found '), ('Fee Structure Not Defined for the selected Class, First Define A Fee Structure.' ))        
        return result
assign_class_to_student()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: