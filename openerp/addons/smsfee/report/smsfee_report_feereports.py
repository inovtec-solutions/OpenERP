import time
from openerp.report import report_sxw
import datetime

class smsfee_report_feereports(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(smsfee_report_feereports, self).__init__(cr, uid, name, context = context)
        self.localcontext.update( {
            'time': time,
            'report_title': self.report_title,
            'get_class_name': self.get_class_name,
            'annual_report_allclasses': self.annual_report_allclasses,
            'annual_report_singleclass': self.annual_report_singleclass,
            'monthly_feecollection_allclasses': self.monthly_feecollection_allclasses,
            'get_month_name':self.get_month_name,
            'students_paidfee_report':self.students_paidfee_report,
            'defaulter_student_list':self.defaulter_student_list,
            'student_fee_receipts':self.student_fee_receipts,
            'daily_fee_report':self.daily_fee_report,
            'company_name':self.company_name,
            'get_user_name':self.get_user_name,
            'get_today':self.get_today,
            'data_ranges':self.data_ranges,
            'student_paidfee_receipts':self.student_paidfee_receipts,
            'annual_defaulter_report_singleclass':self.annual_defaulter_report_singleclass,
            'monthly_feestructure_collections_allclasses': self.monthly_feestructure_collections_allclasses,
            'get_grand_total':self.get_grand_total,
        })
        self.base_amount = 0.00
    
    def report_title(self, data):  
        start_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['from_date'])
        end_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['to_date'])
        string = "Students Admissions \n " +str(start_date) + "-TO -"+str(end_date)
        return string
    
    def get_today(self, data):
        today = datetime.date.today()
#         dated = self.pool.get('sms.session').set_date_format(self.cr,self.uid,today)
        return today
    
    def get_user_name(self, data):
        print "called:......"
        return self.pool.get('res.users').browse(self.cr, self.uid,self.uid).name
    
    def get_class_name(self, data):  
        return self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,self.datas['form']['class_id'][0]).name
    
    def data_ranges(self, data):  
        from_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['from_date'])
        to_date = self.pool.get('sms.session').set_date_format(self.cr, self.uid,self.datas['form']['to_date'])
        range = "From: "+str(from_date)+" To "+str(to_date)
        return range
    
    def company_name(self, data):  
        return self.pool.get('smsfee.classes.fees').get_company(self.cr, self.uid,self.uid)
    
    def get_month_name(self, data):  
        return self.pool.get('sms.session.months').browse(self.cr, self.uid,self.datas['form']['month'][0]).name
    
    def annual_report_allclasses(self, data):                                                         
        result = []
        this_form = self.datas['form']
#         acad_cal = this_form['acad_cal'][0]
        session_id = this_form['session'][0]
        reporttype = this_form['report_type']
#         students = self.pool.get('sms.academiccalendar.student').search(self.cr, self.uid,[('name', '=', acad_cal),('state', '=','Current')])
#       
        session_months_ids = self.pool.get('sms.session.months').search(self.cr, self.uid,[('session_id', '=', session_id)])
        session_months_ids.sort()
        months = self.pool.get('sms.session.months').browse(self.cr, self.uid,session_months_ids)
        mydict = {'sno':'SNO','class':'Class','m1':'','m2':'','m3':'--','m4':'--','m5':'','m6':'','m7':'--','m8':'--','m9':'','m10':'','m11':'--','m12':'--','total':'Total'}
        c = 1
        for mm in months:
            arr = mm.name.split('-')
            mydict['m'+str(c)] = arr[0][:3]+"\n"+arr[1]
            c = c + 1
        result.append(mydict) 
        session_cls_ids = self.pool.get('sms.academiccalendar').search(self.cr, self.uid,[('session_id', '=', session_id)]) 
        classes_list = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,session_cls_ids)
        i = 1
        grand_total = 0
        mydict_total = {'sno':'Total','class':'-','m1':0,'m2':0,'m3':0,'m4':0,'m5':0,'m6':0,'m7':0,'m8':0,'m9':0,'m10':0,'m11':0,'m12':0,'total':0,'gtotal':0}
  
        for cls in classes_list:
            mydict = {'sno':'SNO','class':'Class','m1':'','m2':'','m3':'--','m4':'--','m5':'','m6':'','m7':'--','m8':'--','m9':'','m10':'','m11':'--','m12':'--','total':'','gtotal':''}
            j = 1 
            clsname = cls.name
            mydict['class'] = clsname
            mtotal = 0
            m1total = 0
            for month in session_months_ids:
                                
                sql = """SELECT sum(paid_amount) FROM smsfee_studentfee WHERE state = 'fee_paid'
                         AND paid_amount>0
                         AND acad_cal_id = """+str(cls.id)+"""
                         AND (fee_month = """+str(month)+""" OR due_month = """+str(month)+""")""" 
                self.cr.execute(sql)
                amount = self.cr.fetchone()[0]
                if amount is None:
                    amount = "-"
                    mtotal = mtotal + 0
                else:
                    mtotal = mtotal + int(amount)
                    mydict['m'+str(j)] = '{0:,d}'.format(int(amount))#this actually gives single entry for one class of one month
                    mydict_total['m'+str(j)] = '{0:,d}'.format(int((str(mydict_total['m'+str(j)])).replace(",", "")) + int(amount))
                    mydict['total'] = '{0:,d}'.format(mtotal)#this actually one class total for all months
                    #mydict_total['total'] = int(mydict_total['total']) + int(mtotal) #this is actually annual grand total of all classes for all months 
                    mydict_total['total'] = '{0:,d}'.format(int((str(mydict_total['total'])).replace(",", "")) + int(amount)) #this is actually annual grand total of all classes for all months
                    print " mydict_total['total']; ",  mydict_total['total']
                    print " mtotal; ",  mtotal
                j = j +1
            grand_total = grand_total + mtotal
            
            mydict['sno'] = i
            
            i = i +1    
            mydict['gtotal'] = '{0:,d}'.format(grand_total)
            result.append(mydict)
        
            #mydict['m1'] = '{0:,d}'.format(int(m1total))
        result.append(mydict_total)
        return result
    
    def annual_report_singleclass(self, data):                                                         
        result = []
        this_form = self.datas['form']
        cls_id = this_form['class_id'][0]

        reporttype = this_form['report_type']
        mydict = {'sno':'SNO','month':'Month','ft1':'--','ft2':'--','ft3':'--','ft4':'--','ft5':'--','other':'Others','total':'TOTAL'}
        
        sql_fs = """ SELECT DISTINCT (smsfee_feetypes.id) FROM smsfee_feetypes
                    INNER JOIN smsfee_classes_fees
                    ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                    WHERE  smsfee_classes_fees.academic_cal_id = """+str(cls_id)
        
        self.cr.execute(sql_fs)
        ft_ids = self.cr.fetchall()
        c = 1
        for idss in ft_ids:
            ftname = self.pool.get('smsfee.feetypes').browse(self.cr, self.uid,idss[0]).name
            mydict['ft'+str(c)] = ftname
            c= c + 1
        result.append(mydict)
        
        brw_cls = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,cls_id)
        session_id = brw_cls.session_id.id
        session_months_ids = self.pool.get('sms.session.months').search(self.cr, self.uid,[('session_id', '=', session_id)])
        session_months_ids.sort()
        
        i = 1  
        #grand_total = 0
        mydict_total = {'sno':'Total','month':'-','ft1':0,'ft2':0,'ft3':0,'ft4':0,'ft5':0,'other':0,'total':0}
        
        for month in session_months_ids:
            mydict = {'sno':'SNO','month':'Month','ft1':'--','ft2':'--','ft3':'--','ft4':'--','ft5':'--','other':'','total':'Total','gtotal':''}
            months = self.pool.get('sms.session.months').browse(self.cr, self.uid,month)
            mydict['month'] = months.name
            mydict['sno'] = i
            cal_month = months.session_month_id.id
            cal_year = months.session_year
            month_end =str(cal_year)+"/"+str(self.pool.get('sms.session.months').get_month_end_date(self.cr, self.uid,cal_month,cal_year))
            month_start = str(cal_year)+"/"+str(cal_month)+"/01"
            
            j = 1
            ft_total = 0
            
            for ft in ft_ids:
                subtype = self.pool.get('smsfee.feetypes').browse(self.cr, self.uid,ft[0]).subtype
                sql = """SELECT sum(smsfee_studentfee.paid_amount) FROM smsfee_studentfee
                         INNER JOIN smsfee_classes_fees
                         ON smsfee_classes_fees.id = smsfee_studentfee.fee_type  
                         WHERE smsfee_classes_fees.fee_type_id = """+str(ft[0])+"""
                         AND smsfee_studentfee.state = 'fee_paid'
                         AND acad_cal_id = """+str(cls_id)+"""
                         AND smsfee_studentfee.paid_amount>0
                         AND smsfee_studentfee.due_month = """+str(month)
                                    
                self.cr.execute(sql)
                amount = self.cr.fetchone()[0]
                if amount is None:
                    amount = float(0)
                    mydict['ft'+str(j)] = amount
                else:
                    ft_total = int(ft_total) + int(amount)
                    mydict['ft'+str(j)] = '{0:,d}'.format(int(amount))
                    print ": ", mydict_total['ft'+str(j)]
                    mydict_total['ft'+str(j)] = '{0:,d}'.format(int((str(mydict_total['ft'+str(j)])).replace(",", "")) + int(amount))
 #                   grand_total = grand_total + ft_total
                j = j + 1
            mydict['total'] = '{0:,d}'.format(ft_total)
            mydict_total['total'] = '{0:,d}'.format(int((str(mydict_total['total'])).replace(",", "")) + int(ft_total)) #this is actually annual grand total of all classes for all months 
            i = i + 1
            result.append(mydict)

        result.append(mydict_total)
        return result

    def monthly_feecollection_allclasses(self, data):                                                         
        result = []
        ####
        this_form = self.datas['form']
        session_id = this_form['session'][0]
        classes_ids = self.pool.get('sms.academiccalendar').search(self.cr, self.uid,[('session_id', '=', session_id)])
        classes_rec = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,classes_ids)
        
        ###
        mydict = {'sno':'SNO','class':'Class','ft1':'','ft2':'','ft3':'','ft4':'','ft5':'','other':'Others','total':'TOTAL'}
        
        sql_fs = """ SELECT  smsfee_feetypes.id FROM smsfee_feetypes"""
        self.cr.execute(sql_fs)
        ft_ids = self.cr.fetchall()
        
        c = 1
        for idss in ft_ids:
            ftname = self.pool.get('smsfee.feetypes').browse(self.cr, self.uid,idss[0]).name
            mydict['ft'+str(c)] = ftname
            c= c + 1
        result.append(mydict)
        ############################################################################################################################
        
        cal_month = self.pool.get('sms.session.months').browse(self.cr, self.uid,self.datas['form']['month'][0])
        cal_month_id = cal_month.session_month_id.id
        cal_year = cal_month.session_year
        month_end =str(cal_year)+"/"+str(self.pool.get('sms.session.months').get_month_end_date(self.cr, self.uid,cal_month_id,cal_year))
        print "month end:",month_end
        month_start = str(cal_year)+"/"+str(cal_month_id)+"/01"
        print "month state:",month_start
        
        i = 1  
        #gtotal = 0
        mydict_total = {'sno':'Total','class':'-','ft1':0,'ft2':0,'ft3':0,'ft4':0,'ft5':0,'other':0,'total':0}
        for cls in classes_rec:
            mydict = {'sno':'SNO','class':'Class','ft1':'','ft2':'','ft3':'','ft4':'','ft5':'','other':'','total':0,'gtotal':0}
            mydict['class'] = cls.name
            mydict['sno'] = i
            j = 1
            ft_total = 0
            
            for ft in ft_ids:
                sql = """SELECT sum(smsfee_studentfee.paid_amount) FROM smsfee_studentfee
                     INNER JOIN smsfee_classes_fees
                     ON smsfee_classes_fees.id = smsfee_studentfee.fee_type  
                     WHERE smsfee_classes_fees.fee_type_id = """+str(ft[0])+"""
                     AND smsfee_studentfee.state = 'fee_paid'
                     AND acad_cal_id = """+str(cls.id)+"""
                     AND smsfee_studentfee.paid_amount>0
                     AND smsfee_studentfee.due_month = """+str(self.datas['form']['month'][0])
                self.cr.execute(sql)
                amount = self.cr.fetchone()[0]
                if amount is None:
                    amount = 0
                else:    
                    ft_total = int(ft_total) + int(amount)
                    mydict['ft'+str(j)] = '{0:,d}'.format(int(amount))
                    mydict_total['ft'+str(j)] = '{0:,d}'.format(int((str(mydict_total['ft'+str(j)])).replace(",", "")) + int(amount))
                j = j + 1
            #gtotal = gtotal + ft_total     
            mydict['total'] = '{0:,d}'.format(ft_total)
            mydict_total['total'] = '{0:,d}'.format(int((str(mydict_total['total'])).replace(",", "")) + int(ft_total))
            #mydict['gtotal'] = '{0:,d}'.format(gtotal)
            i = i + 1
            result.append(mydict)
        result.append(mydict_total)
        return result
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def students_paidfee_report(self, data):                                                         
        result = []
        ####
        this_form = self.datas['form']
        cls_id = this_form['class_id'][0]
        std_ids = self.pool.get('sms.student').search(self.cr, self.uid,[('current_class', '=', cls_id)])
        students_rec = self.pool.get('sms.student').browse(self.cr, self.uid,std_ids)
        
        ###
        mydict = {'sno':'SNO','student':'Student','father':'Father','ft1':'','ft2':'','ft3':'','ft4':'','ft5':'','other':'','total':'TOTAL','gtotal':''}
        
        sql_fs = """ SELECT DISTINCT smsfee_feetypes.id,smsfee_feetypes.subtype  FROM smsfee_feetypes
                     INNER JOIN smsfee_classes_fees
                     ON smsfee_feetypes.id = smsfee_classes_fees.fee_type_id
                     WHERE  smsfee_classes_fees.academic_cal_id = """+str(cls_id)
        self.cr.execute(sql_fs)
        ft_ids = self.cr.fetchall()
        
        c = 1
        for idss in ft_ids:
            ftname = self.pool.get('smsfee.feetypes').browse(self.cr, self.uid,idss[0]).name
            mydict['ft'+str(c)] = ftname
            c= c + 1
        result.append(mydict)
        ############################################################################################################################
        
        cal_month = self.pool.get('sms.session.months').browse(self.cr, self.uid,self.datas['form']['month'][0])
        cal_month_id = cal_month.session_month_id.id
        cal_year = cal_month.session_year
        month_end =str(cal_year)+"/"+str(self.pool.get('sms.session.months').get_month_end_date(self.cr, self.uid,cal_month_id,cal_year))
        month_start = str(cal_year)+"/"+str(cal_month_id)+"/01"
        
        i = 1
        #grand_total = 0
        mydict_total = {'sno':'Total','class':'-','ft1':0,'ft2':0,'ft3':0,'ft4':0,'ft5':0,'other':0,'total':0}   
        for student in students_rec:
            mydict = {'sno':'SNO','student':'Student','father':'Father','ft1':'','ft2':'','ft3':'','ft4':'','ft5':'','other':'','total':float(0)}
            mydict['student'] = student.name
            mydict['father'] = student.father_name
            mydict['sno'] = i
            j = 1
            ft_total = 0
            for ft in ft_ids:
                mydict['ft'+str(j)] = '-'
                sql = """SELECT smsfee_studentfee.paid_amount,smsfee_studentfee.state FROM smsfee_studentfee
                         INNER JOIN smsfee_classes_fees
                         ON smsfee_classes_fees.id = smsfee_studentfee.fee_type  
                         WHERE smsfee_classes_fees.fee_type_id = """+str(ft[0])+"""
                         AND smsfee_studentfee.student_id = """+str(student.id)+"""
                         AND smsfee_studentfee.acad_cal_id = """+str(cls_id)+"""
                         AND smsfee_studentfee.due_month = """+str(self.datas['form']['month'][0])
                
                self.cr.execute(sql)
                rows = self.cr.fetchone()
                if rows: #if rows is not empty ie not none and contains a list
                    amount = rows[0] #then assign the value at index 0 of rows list
                    if amount is None and not rows[1]=='fee_paid':#if the assigned value to amount is None and not the value at index 1 of rows list then assign 0 to amount
                        amount  = int(0)
                    mydict['ft'+str(j)] = '{0:,d}'.format(amount)#if the value at index [0] assigned to amount fails to satisfy this condition "if amount is None and not rows[1]" then assign it to ft1, ft2..etc 
                    mydict_total['ft'+str(j)] = '{0:,d}'.format(int((str(mydict_total['ft'+str(j)])).replace(",", "")) + int(amount))
                    ft_total = int(ft_total) + int(amount)
                    mydict['total'] = '{0:,d}'.format(ft_total)
                    mydict_total['total'] = '{0:,d}'.format(int((str(mydict_total['total'])).replace(",", "")) + int(ft_total))
                    
                    #grand_total = grand_total + ft_total
                       
                else:
                    mydict['ft'+str(j)] ='---'
                
                j = j + 1
            
            i = i + 1
            result.append(mydict)
            #mydict['gtotal'] = grand_total
        result.append(mydict_total)
        return result
    
#--------------------------------------------------------------------------------------------------------------------------------------------------------    

#     def monthwise_defaulter_studentslist(self, data):                                                         
#             result = []
#             """Late fee amount is not shown. to show it, make another columns on right side of others and mention it in separate column"""
#             this_form = self.datas['form']
#             session_id = this_form['session']
#            cls_id = this_form['class_id'][0]class_id
#             print "AAAAAAAAAA>>>>>>",session_id
#             acad_ids = self.pool.get('sms.session').search(self.cr, self.uid,[('acad_cals', '=', session_id)])
#             print "BBBBBBBBBBBBBBB>>>>>>", acad_ids
#             cls_id = self.pool.get('sms.session').search(self.cr, self.uid,[('name', '=', acad_ids)])
#             print "CCCCCCCCCCCCCCC>>>>>>", acad_ids
    def defaulter_student_list(self, data):                                                         
            result = []
            """Late fee amount is not shown. to show it, make another columns on right side of others and mention it in separate column"""
            this_form = self.datas['form']
            cls_id = this_form['class_id'][0]
            students_cad_id = self.pool.get('sms.student').search(self.cr, self.uid,[('current_class', '=', cls_id)], order='name')
            students_acad_rec = self.pool.get('sms.student').browse(self.cr, self.uid,students_cad_id)
        

            i = 1    
            for student in students_acad_rec:
                mydict = {'sno':'SNO','student':'Student','father':'Father','fee_amount':'--','remarks':'Remarks','total':'TOTAL'}
                mydict['father'] = student.father_name
                mydict['sno'] = i
                paybles = 0
                fee_amount = float(0)
                rec = float(0)
                all_monthly_paid = True
                sql = """SELECT sum(fee_amount) from smsfee_studentfee
                         WHERE  smsfee_studentfee.student_id = """+str(student.id)+"""
                         AND state = 'fee_unpaid'
                         """
                self.cr.execute(sql)
                rec = self.cr.fetchone()     
                if rec[0] > 0:
                    fee_amount = rec[0]
                    mydict['student'] = student.name
                    mydict['fee_amount'] = '{0:,d}'.format(fee_amount)#the variable fee_amout hold the value and '{0:,d}'.format(variable) converts it to cureency format
                    result.append(mydict)
                    i = i + 1
                
            return result
#---------------------------------------------------------------------------------------------------------------------------------------------------

    def student_fee_receipts(self, data):                                                         
            result = []
            """student unpaid fee receipt"""
            std_ids = self.ids
            if not std_ids:
                this_form = self.datas['form']
                print "this form:",this_form
                cls_id = this_form['class_id'][0]
                dated = this_form['today']
                std_ids = self.pool.get('sms.student').search(self.cr, self.uid,[('current_class', '=', cls_id)])
                students_rec = self.pool.get('sms.student').browse(self.cr, self.uid,std_ids)
            else:
                dated = datetime.date.today()
                print "idss:",std_ids
                students_rec = self.pool.get('sms.student').browse(self.cr, self.uid,std_ids)
#                 cls_id = students_rec.current_class.id
            i = 1    
            for student in students_rec:
                class_rec = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,student.current_class.id)
                print "dyf curr class:",student.current_class
                cls_id = class_rec.id
                print "class id:",cls_id
                mydict = {'student':'Student','feestrc':'','father':'Father','class':'Class','dated':dated,'duedate':'due_date','total':'total','fee_arr':''}
                fs = self.pool.get('sms.feestructure').browse(self.cr, self.uid,student.fee_type.id).name
                mydict['sno'] = i
                mydict['student'] = student.name
                mydict['feestrc'] = fs
                mydict['father'] = student.father_name
                mydict['class'] = class_rec.name
                mydict['dated'] = dated
                
                sql = """SELECT smsfee_studentfee.fee_amount, smsfee_studentfee.fee_type,
                         smsfee_studentfee.fee_month  FROM smsfee_studentfee
                         INNER JOIN smsfee_classes_fees
                         ON smsfee_classes_fees.id = smsfee_studentfee.fee_type  
                         WHERE smsfee_studentfee.student_id = """+str(student.id)+"""
                         AND smsfee_studentfee.state = 'fee_unpaid'"""
                self.cr.execute(sql)
                rec = self.cr.fetchall() 
                total = 0
                result2 = []
                if rec:
                    j = 1
                    for fees in rec:
                        print "fees: ", fees
                        total = total +fees[0]
                        fee_dic = {'sno':'','fee_name':'','amount':''} 
                        fee_dic['sno'] = j
                        if fees[0] ==0:
                            fee_dic['amount'] = "0"
                        else:
                            fee_dic['amount'] = fees[0]    
                        fee_name = self.pool.get('smsfee.classes.fees').browse(self.cr, self.uid,fees[1] ).name
                        if fees[2]:
                           fee_month =  self.pool.get('sms.session.months').browse(self.cr, self.uid,fees[2] ).name
                           fee_name = fee_name+"("+fee_month+")"
                        fee_dic['fee_name'] = fee_name
                        result2.append(fee_dic)
                        j = j + 1
                    
                    mydict['total'] = total
                    mydict['fee_arr'] = result2        
                    i = i + 1
                    print "result2: ", result2
                    result.append(mydict)
            return result
#------------------------------------------------------------------------------------------------------------------------------------------
    def daily_fee_report(self, data):                                                         
        result = []
        ####
        this_form = self.datas['form']
        cls_id = this_form['class_id']
        fee_manager = this_form['fee_manager']
        if cls_id:
            this_form['class_id'][0]
            cls_qry = """AND student_class_id= """+str(this_form['class_id'][0])
        else:
            cls_qry = """ """ 
        if fee_manager:
             fm_query = """AND fee_received_by = """+str(this_form['fee_manager'][0])  
        else:
             fm_query ="""""" 
        print "class ids:",cls_id
        
        ###
        
        
        sql_rb = """ SELECT total_paid_amount,student_class_id,student_id,fee_received_by,receipt_date,
                     name FROM smsfee_receiptbook                              
                     WHERE smsfee_receiptbook.receipt_date >= '"""+str(this_form['from_date'])+"""'
                     AND smsfee_receiptbook.receipt_date <= '"""+str(this_form['to_date'])+"""'
                     """+cls_qry+"""
                     """+fm_query+"""
                     AND smsfee_receiptbook.state='Paid'
                     AND smsfee_receiptbook.total_paid_amount>0 ORDER By receipt_date """
                             
        self.cr.execute(sql_rb)
        rb_ids = self.cr.fetchall()
        c = 1
        dict1 = {'total_amount':'','arr':''}
        total_amount = 0
        result2 = []
        for idss in rb_ids:
            mydict = {'sno':'SNO','paid_amount':'class_name','student_name':'fee_received_by','receipt_date':'','receipt_no':''}
            student_name = self.pool.get('sms.student').browse(self.cr, self.uid,idss[2]).name
            class_name = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,idss[1]).name
            user = self.pool.get('res.users').browse(self.cr, self.uid,idss[3]).name
            total_amount = total_amount + idss[0]
            dated = self.pool.get('sms.session').set_date_format(self.cr, self.uid,idss[4])
            mydict['sno'] = c
            mydict['receipt_date'] = dated
            mydict['paid_amount'] = idss[0]
            mydict['class_name'] = class_name
            mydict['student_name'] = student_name
            mydict['fee_received_by'] = user
#             mydict['receipt_no'] = idss[5]
            c= c + 1
            result2.append(mydict)
        dict1['arr'] = result2 
        dict1['total_amount'] = total_amount  
        result.append(dict1)
        return result
#--------------------------------------------------------------------------------------------------------------------------------------
    def student_paidfee_receipts(self, data):                                                         
                result = []
                result2 = []
                """student paid fee receipt from receiptbook"""
                rec = self.pool.get('smsfee.receiptbook').browse(self.cr, self.uid,self.ids[0])
                cls_id = rec.student_class_id.id
                dated = rec.receipt_date
                class_rec = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,cls_id)
                std_ids = self.pool.get('sms.student').search(self.cr, self.uid,[('current_class', '=', cls_id)])
                students_rec = self.pool.get('sms.student').browse(self.cr, self.uid,rec.student_id.id)
                
                mydict = {'student':'Student','feestrc':'','father':'Father','class':'Class','r_no':'','received_by':'','dated':dated,'duedate':'due_date','total':'total','fee_arr':''}
                fs = self.pool.get('sms.feestructure').browse(self.cr, self.uid,students_rec.fee_type.id).name
                mydict['student'] = students_rec.name 
                mydict['feestrc'] = fs
                mydict['r_no'] = 'No:\t'+str(rec.name)
                mydict['received_by'] = self.pool.get('res.users').browse(self.cr, self.uid,rec.fee_received_by.id).name
                mydict['father'] = 'Father:\t'+str(students_rec.father_name)
                mydict['class'] = class_rec.name
                mydict['dated'] = 'Date:\t'+str(dated)
                    
                lines_ids = self.pool.get('smsfee.receiptbook.lines').search(self.cr, self.uid,[('receipt_book_id', '=', self.ids[0]),('reconcile', '=', True)])
                j = 1
                total_dues = 0
                total_discount = 0
                total_paid = 0
                for lines in lines_ids:
                    print "fees: ", lines
                    lines_rec = self.pool.get('smsfee.receiptbook.lines').browse(self.cr, self.uid,lines)
                    ft = self.pool.get('smsfee.classes.fees').browse(self.cr,self.uid, lines_rec.fee_type.id)
                    fm_id = lines_rec.fee_month.id
                    print fm_id 
                    if fm_id:
                        fm = self.pool.get('sms.session.months').browse(self.cr,self.uid,fm_id)
                        print "fee_month:",fm.name
                        ft_name = ft.name+"("+str(fm.name)+")"
                    else:
                        ft_name = ft.name 
                    fee_dic = {'sno':'','fee':'','fee_amount':'','discount':'','paid_amount':''} 
                    fee_dic['sno'] = j
                    fee = lines_rec.fee_amount
                    if fee == 0:
                        fee = '0'
                    fee_dic['fee'] = ft_name
                    fee_dic['fee_amount'] =fee
                    discount = lines_rec.discount
                    if discount == 0:
                        discount = '0'
                    fee_dic['discount'] = discount
                    paid_amount = lines_rec.paid_amount
                    if paid_amount == 0:
                       paid_amount = '0'
                    fee_dic['paid_amount'] = paid_amount
                    total_paid = total_paid + lines_rec.paid_amount
                    
                     
#                     fee_name = self.pool.get('smsfee.classes.fees').browse(self.cr, self.uid,fees[1] ).name
#                     if fees[2]:
#                        fee_month =  self.pool.get('sms.session.months').browse(self.cr, self.uid,fees[2] ).name
#                        fee_name = fee_name+"("+fee_month+")"
#                     fee_dic['fee_name'] = fee_name
                    result2.append(fee_dic)
                    j = j + 1
                
#                 mydict['total'] = total
                mydict['total'] = total_paid 
                mydict['fee_arr'] = result2        
                print "result2: ", result2
                result.append(mydict)
                return result
 #------------------------------------------------------------------------------------------------------------------------------------------
    def annual_defaulter_report_singleclass(self, data):                                                         
            result = []
            this_form = self.datas['form']
    #         acad_cal = this_form['acad_cal'][0]
            session_id = this_form['session'][0]
            class_id = this_form['class_id'][0]
            reporttype = this_form['report_type']
    #         students = self.pool.get('sms.academiccalendar.student').search(self.cr, self.uid,[('name', '=', acad_cal),('state', '=','Current')])
    #       
            session_months_ids = self.pool.get('sms.session.months').search(self.cr, self.uid,[('session_id', '=', session_id)])
            session_months_ids.sort()
            months = self.pool.get('sms.session.months').browse(self.cr, self.uid,session_months_ids)
            mydict = {'sno':'SNO','name':'Name','m1':'--','m2':'--','m3':'--','m4':'--','m5':'','m6':'','m7':'--','m8':'--','m9':'','m10':'','m11':'--','m12':'--','session_total':'Session Total','other':'Others','total':'Total'}
            c = 1
            for mm in months:
                arr = mm.name.split('-')
                mydict['m'+str(c)] = arr[0][:3]+"\n"+arr[1]
                c = c + 1
            result.append(mydict) 
            
            sql = """select sms_academiccalendar_student.id from sms_student
                     inner join sms_academiccalendar_student on
                     sms_student.id = sms_academiccalendar_student.std_id
                     WHERE sms_academiccalendar_student.name = """ + str(class_id) +"""
                     ORDER by sms_student.name"""
                     #sql takes ids from sms_academiccalendar_student on the basis of class_id and orders it by name field of sms_student which has inner join with sms_academiccalendar_student on foreign key std_id
            self.cr.execute(sql)
            students_list = self.cr.fetchall()

            students_cls_ids = []
            for sname in students_list:
                students_cls_ids.append(sname[0]) #student_list contains tuples
            students_obj = self.pool.get('sms.academiccalendar.student').browse(self.cr, self.uid,students_cls_ids)
            
            
            i = 1
            grand_total = 0
            #             for sname in students_list:
            mydict_total = {'sno':'Total','class':'-','m1':0,'m2':0,'m3':0,'m4':0,'m5':0,'m6':0,'m7':0,'m8':0,'m9':0,'m10':0,'m11':0,'m12':0,'session_total':0,'other':0,'total':0}
            for std in students_obj:
                mydict = {'sno':'SNO','name':'Name','m1':'--','m2':'--','m3':'--','m4':'--','m5':'','m6':'','m7':'--','m8':'--','m9':'','m10':'','m11':'--','m12':'--','session_total':'0','other':'--','total':'--','gtotal':''}
                stdid = std.std_id.id
           
#                stdid = std.std_id.id
#                stdrec = self.pool.get('sms.student').browse(self.cr, self.uid,stdid)
#                print "stdnamedddd:", stdrec.name

                mydict['name'] = std.std_id.name
                mtotal = 0
                others = 0
                stotal = 0
                
                j = 1
                for month in session_months_ids:
                    sql = """SELECT sum(fee_amount) FROM smsfee_studentfee WHERE state = 'fee_unpaid'
                        AND acad_cal_id = """+str(class_id)+"""
                        AND student_id = """+str(stdid)+"""
                        AND due_month = """+str(month) 
                        
                    self.cr.execute(sql)
                    amount = self.cr.fetchone()[0]
                    if amount is None:
                        amount = "-"
                        mtotal = mtotal + 0
                    else:
                        mtotal = mtotal + int(amount)
                        if mtotal> 0:
                            mydict['m'+str(j)] = '{0:,d}'.format(amount) #the variable amount hold the value and '{0:,d}'.format(variable) converts it to currency format
                            mydict_total['m'+str(j)] = '{0:,d}'.format(int((str(mydict_total['m'+str(j)])).replace(",", "")) + int(amount))
                            mydict['session_total'] = '{0:,d}'.format(mtotal)#the variable mtotal hold the value and '{0:,d}'.format(variable) converts it to currency format
                            mydict_total['session_total'] = '{0:,d}'.format(int((str(mydict_total['session_total'])).replace(",", "")) + int(amount)) #this is actually annual grand total of all classes for all months 
                    j = j +1
                
                sql = """SELECT sum(fee_amount) FROM smsfee_studentfee WHERE state = 'fee_unpaid'
                    AND acad_cal_id != """+str(class_id)+"""
                    AND student_id = """+str(stdid)
                self.cr.execute(sql)
                others = self.cr.fetchone()[0]
                if others is None:
                    others = "-"
                    stotal = mtotal + 0
                else:
                    mydict['other'] = '{0:,d}'.format(others)#the variable others hold the value and '{0:,d}'.format(variable) converts it to currency format                            
                    mydict_total['other'] = '{0:,d}'.format(int((str(mydict_total['other'])).replace(",", "")) + int(others)) #this is actually annual grand total of all classes for all months
                    stotal = others + mtotal
                mydict['total'] = '{0:,d}'.format(stotal)#the variable stotal hold the value and '{0:,d}'.format(variable) converts it to currency format
                mydict_total['total'] = '{0:,d}'.format(int((str(mydict_total['total'])).replace(",", "")) + int(stotal)) #this is actually annual grand total of all classes for all months
                grand_total = grand_total + stotal
                mydict['sno'] = i
           
                i = i +1    
                result.append(mydict)
                mydict['gtotal'] = '{0:,d}'.format(grand_total)#the variable grand_total hold the value and '{0:,d}'.format(variable) converts it to cureency format
            result.append(mydict_total)         
            return result

#-----------------------------------------------------------------------------------------------------------------------------
    def monthly_feestructure_collections_allclasses(self, data):                                                         
        result = []
        this_form = self.datas['form']
        session_id = this_form['session'][0]
        classes_ids = self.pool.get('sms.academiccalendar').search(self.cr, self.uid,[('session_id', '=', session_id)])
        classes_rec = self.pool.get('sms.academiccalendar').browse(self.cr, self.uid,classes_ids)
        
        sql_fs = """ SELECT  sms_feestructure.id FROM sms_feestructure"""
        self.cr.execute(sql_fs)
        fst_ids = self.cr.fetchall()
        
#         cal_month = self.pool.get('sms.session.months').browse(self.cr, self.uid,self.datas['form']['month'][0])
#         cal_month_id = cal_month.session_month_id.id
#         cal_year = cal_month.session_year
#         month_end =str(cal_year)+"/"+str(self.pool.get('sms.session.months').get_month_end_date(self.cr, self.uid,cal_month_id,cal_year))
#         month_start = str(cal_year)+"/"+str(cal_month_id)+"/01"
        
#         sql = """SELECT academic_cal_id, fee_structure_id, sum(smsfee_studentfee.paid_amount) as sum,
#            (select name from sms_academiccalendar where id = academic_cal_id), 
#            (select name from sms_feestructure where id = fee_structure_id),
#            (select name from sms_session_months where id = due_month)   
#            FROM smsfee_studentfee
#            INNER JOIN smsfee_classes_fees
#            ON smsfee_classes_fees.id = smsfee_studentfee.fee_type  
#            group by academic_cal_id,fee_structure_id,due month
#            order by academic_cal_id,fee_structure_id,due_month"""

        sql = """SELECT academic_cal_id, fee_structure_id, sum(smsfee_studentfee.paid_amount) as sum,
             (select name from sms_academiccalendar where id = academic_cal_id), 
             (select name from sms_feestructure where id = fee_structure_id)
             FROM smsfee_studentfee
             INNER JOIN smsfee_classes_fees
             ON smsfee_classes_fees.id = smsfee_studentfee.fee_type
             WHERE smsfee_studentfee.date_fee_paid >= '"""+str(this_form['from_date'])+"""'
             AND smsfee_studentfee.date_fee_paid <= '"""+str(this_form['to_date'])+"""'
             group by fee_structure_id, academic_cal_id
             order by academic_cal_id,fee_structure_id"""

        self.cr.execute(sql)
        records = self.cr.fetchall()                
        j = 1
        total = 0
        for record in records:
            mydict = {'sno':'SNO','class':'','fee_structure':'','fee_type':'','amount':''}
            mydict['sno'] = j
            mydict['class'] = record[3]
            mydict['fee_structure'] = record[4]
#            mydict['fee_type'] = record[4]
            mydict['amount'] = record[2]
            j = j + 1
            result.append(mydict)
            total = total + int(record[2])
        
        mydict = {'sno':'Total','class':'','fee_structure':'','fee_type':'','amount':total}
        result.append(mydict)
        return result
    
    def get_grand_total(self, data):
        this_form = self.datas['form']                                                         
        sql = """SELECT sum(smsfee_studentfee.paid_amount) as sum FROM smsfee_studentfee
            WHERE smsfee_studentfee.date_fee_paid >= '"""+str(this_form['from_date'])+"""'
            AND smsfee_studentfee.date_fee_paid <= '"""+str(this_form['to_date'])+"""'
            smsfee_studentfee.state = 'fee_paid'"""
        self.cr.execute(sql)
        return self.cr.fetchone()[0]                

#-------------------------------------------------------------------------------      
        
report_sxw.report_sxw('report.smsfee_annaul_defaulter_list_name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_annual_defaulter_list.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee.annaul.allclasses.name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_annual_allclasses.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee.annaul.singleclass.name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_annual_singleclass.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee.monthlyfeecollection.allclasses.name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_monthly_feecollection_allclasses.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee.monthly.feestructure.collections.allclasses.name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_monthly_feestructure_collections_allclasses.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee_students_paidfee_report_name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_students_paid_fee_report.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee_defaulter_studnent_list_name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_defaulter_student_list_report.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee_unpaidfee_receipt_name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_unpaid_receipts_report.rml',parser = smsfee_report_feereports, header=None)
report_sxw.report_sxw('report.smsfee.dailyfee.report.name', 'smsfee.classfees.register', 'addons/smsfee/smsfee_dailyfee_report.rml',parser = smsfee_report_feereports, header='external')
report_sxw.report_sxw('report.smsfee.paidfee.receipt.name', 'smsfee.receiptbook', 'addons/smsfee/print_paid_receipt_individual.rml',parser = smsfee_report_feereports, header='external')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

