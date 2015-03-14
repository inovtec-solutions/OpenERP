from openerp.osv import fields, osv
import datetime

class update_fee_register(osv.osv_memory):

    def _get_thisclass(self, cr, uid, ids):
        clsobj = self.browse(cr, uid, ids['active_id'])
        cls_id =  clsobj.id
        return cls_id
    
        
    def _get_fee_month(self, cr, uid, ids):
        clsobj = self.browse(cr, uid, ids['active_id'])
        acad_cal = self.pool.get('sms.academiccalendar').browse(cr,uid,clsobj.id)
        month_id =  acad_cal.fee_update_till.id
        if month_id:
           return month_id
        else:
            return 0
    
    def _get_class_session(self, cr, uid, ids):
        clsobj = self.browse(cr, uid, ids['active_id'])
        acad_cal = self.pool.get('sms.academiccalendar').browse(cr,uid,clsobj.id)
        session_id =  acad_cal.session_id.id
        return session_id
        
    
    _name = "update.fee.register"
    _description = "Update monthly class register"
    _columns = {
              'action':fields.selection([('update_class_monthly_fee', 'Update Monthly Fees Register'),('add_fee', 'Add Fee To Class')], 'Action', required = True),      
              'session': fields.many2one('sms.session', 'Session', domain="[('state','!=','Previous')]",readonly = True,help="Select an academic session"),
              "name": fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active'),('fee_defined','=',1)]", readonly=True, help="Select A class to load its subjects."),
              'fee_type':fields.many2one('smsfee.feetypes', 'Fee', domain="[('subtype','=','Other')]"),
              'fee_amount':fields.float('Amount'),
              "updated_till": fields.many2one('sms.session.months', 'Upadted Till',readonly=True, help="Class Session."),
              'update_upto': fields.many2one('sms.session.months', 'Update Upto', domain="[('session_id','=',session)]" ,help="Fee Is update upto shown month."),
              'month_of_dues': fields.many2one('sms.session.months', 'Dues Month', domain="[('session_id','=',session)]" ,help="Fee Is update upto shown month."),
               }
    _defaults = {
          'name':_get_thisclass,
          'session':_get_class_session,
          'updated_till':_get_fee_month,
           }
    
    
    
    def update_feeregister(self, cr, uid, ids, data):
        result = []
        for f in self.browse(cr, uid, ids):
            action = f.action
            acad_cal =f.name.id 
            if action == 'update_class_monthly_fee':
                 
                update_upto = f.update_upto.id
                acad_cal_obj = self.pool.get('sms.academiccalendar').browse(cr,uid,acad_cal)
                session_id =  acad_cal_obj.session_id.id
               
                #months to be updated
                months_id = self.pool.get('sms.session.months').search(cr,uid,[('session_id','=',session_id)])
                #student of current semeste with their fee structure
                acad_cal_stds = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('name','=',acad_cal),('state','=','Current')])
                cal_std_objs = self.pool.get('sms.academiccalendar.student').browse(cr,uid,acad_cal_stds)
                # Get fee types from smsfee with type monthly fee.
    #             fee_type_ids = 
                for month in months_id:
                    # check if month for given class is already updated
                    month_exists = self.pool.get('smsfee.classfees.register').search(cr,uid,[('month','=',month),('academic_cal_id','=',acad_cal)])
                    if not month_exists:
                        if month <= update_upto:
                            print "month>>>>>>",month
                            updated_fee_till = month
                            for cal_std_obj in cal_std_objs:
                                #print "cal_std_id",cal_std_id
                                #cal_std_obj = self.pool.get('sms.academiccalendar.student').browse(cr,uid,cal_std_id)
                                #print "std_id1",cal_std_obj.std_id
                                std_id = cal_std_obj.std_id.id
                                if not std_id:
                                    continue
                                std_obj = self.pool.get('sms.student').browse(cr,uid,std_id)
                                std_feestr = std_obj.fee_type.id
                                total_paybles = std_obj.total_paybles
                                # get monthly fees from classes fee with fee structure define with student,with subtype monthly fee
    #                             monthly_feeids = self.pool.get('smsfee.classes.fees').search(cr,uid,[('fee_structure_id','=',std_feestr),('academic_cal_id','=',acad_cal),('fee_type_subtype','=','Monthly_Fee')])
                                                               
                                ft_idss2 = self.pool.get('smsfee.feetypes').search(cr,uid,[('subtype','=','Monthly_Fee')])
                                for ft in ft_idss2:
                                    sqlfee2 = """SELECT smsfee_classes_fees.id from smsfee_classes_fees
                                                INNER JOIN smsfee_feetypes
                                                on smsfee_feetypes.id = smsfee_classes_fees.fee_type_id WHERE
                                                academic_cal_id ="""+str(acad_cal)+""" AND fee_structure_id="""+str(std_feestr)+"""
                                                AND smsfee_feetypes.id ="""+str(ft)+""""""
                                    cr.execute(sqlfee2)
                                    monthly_feeids = cr.fetchall()
                                     
                                    for feetype in monthly_feeids:
                                        print "fee type id::",feetype[0]
                                        cls_fee_obj = self.pool.get('smsfee.classes.fees').browse(cr,uid,feetype[0])
                                        print "fee_month:",month
                                        print "std_id:",std_id
                                        print "fts:",ft
                                        #check if student is already charged with fee then only uodate record otherwiase insert his fee    
                                        std_fee_ids = self.pool.get('smsfee.studentfee').search(cr,uid,[('student_id','=',std_id),('generic_fee_type','=',ft),('fee_month','=',month)])
                                        if not std_fee_ids:
                                            std_fee_obj = self.pool.get('smsfee.studentfee').create(cr,uid,{
                                                                'acad_cal_id':acad_cal,                                                       
                                                                'student_id':std_id,
                                                                'acad_cal_std_id':cal_std_obj.id,
                                                                'date_fee_charged':datetime.date.today(),
                                                                'fee_type':feetype[0],
                                                                'generic_fee_type':ft,
                                                                'fee_month':month,
                                                                'due_month':month, 
                                                                'fee_amount':cls_fee_obj.amount,
                                                                'total_amount':cls_fee_obj.amount,                                                       
                                                                'net_total':cls_fee_obj.amount,
                                                                'reconcile':False,
                                                                'state':'fee_unpaid',
                                                                })
                                    
                                #update register object ofr this month
                            fee_register = self.pool.get('smsfee.classfees.register').create(cr,uid,{
                                                            'academic_cal_id':acad_cal,                                                       
                                                            'month':month, 
                                                                }) 
                            updated_till = self.pool.get('sms.academiccalendar').write(cr,uid,[acad_cal],{'fee_update_till':month})
                    else:
                        print "this month is already updated ",month
            elif action == 'add_fee':
                 sql="""delete from smsfee_fee_adjustment where user_id = """+str(uid)
                 cr.execute(sql)
                 cr.commit()
                 print "adding fee to class"
                 #add Fee to the whole class normally the fee may be of type other, but it also contain more fee types
                 acad_cal_stdids = self.pool.get('sms.academiccalendar.student').search(cr,uid,[('state','=','Current'),('name','=',acad_cal)])
                 acad_cal_stdids_rec = self.pool.get('sms.academiccalendar.student').browse(cr,uid,acad_cal_stdids)
                 fee_subtype = self.pool.get('smsfee.feetypes').browse(cr,uid,f.fee_type.id).subtype
                
                 for idss in acad_cal_stdids_rec:
                     student_rec = self.pool.get('sms.student').browse(cr,uid,idss.std_id.id)
                     if fee_subtype == 'Other':
                         classes_fee = self.pool.get('smsfee.classes.fees').search(cr, uid, [('fee_type_id','=',f.fee_type.id),('academic_cal_id','=',acad_cal),('fee_structure_id','=',student_rec.fee_type.id)])
                         if classes_fee:
                             amount = self.pool.get('smsfee.classes.fees').browse(cr,uid,classes_fee[0]).amount
                         else:
                              raise osv.except_osv(('No Fee Found For Selected Class'),('Please Define a Fee For Selected Class'))
                     else:
                         amount = f.fee_amount
                     print "found students",idss.std_id.id
                     print "due_month",f.month_of_dues.id
                     print "fee_structure",student_rec.fee_type.id
                     print "amount",f.fee_amount
                     print "class_id",acad_cal
                     print "action",action
                     std_fee_obj = self.pool.get('smsfee.fee.adjustment').create(cr,uid,{
                                      'class_id':acad_cal,                                                       
                                      'name':idss.std_id.id,
                                      'student_class_id':idss.id,
                                      'fee_structure':student_rec.fee_type.id,
                                      'due_month':f.month_of_dues.id, 
                                      'fee_type': f.fee_type.id,
                                      'fee_subtype':fee_subtype,
                                      'amount':amount,
                                      'selected':False,
                                      'user_id':uid,
                                      'action':'add_fee'
                                      })
        
                 cr.execute("""select id,name from ir_ui_view 
                        where model= 'smsfee.fee.adjustment' 
                        and type='tree'""")
                 view_res = cr.fetchone()
                 return {
                #'domain': "[('parent_default_exam','=',"+str(sms_temp_new_id)+")]",
                'name': 'Add Fee To Class: ' +  str(f.name.name)+'\n'+str(f.fee_type.name),
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'smsfee.fee.adjustment',
                'view_id': view_res,
                'type': 'ir.actions.act_window'}             
update_fee_register()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: