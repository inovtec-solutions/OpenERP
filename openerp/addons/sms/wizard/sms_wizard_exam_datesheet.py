from openerp.osv import fields, osv
import datetime

class exam_datesheet(osv.osv_memory):
    
    def _get_exam_offered(self, cr, uid, context=None):
        print "context['active_ids']: ", context['active_ids'][0]
        return context['active_ids'][0]
    
    _name = "exam.datesheet"
    _description = "Exam Date Sheet"
    _columns = {
                 'exam_offered': fields.many2one('sms.exam.offered', 'Select Offered Exam', domain="[('state','in',['Active','Draft'])]", required=True, readonly=True),
                 'academiccalendar':fields.many2one('sms.academiccalendar', 'Class', domain="[('state','=','Active')]", required=True),
                 'subject_marks':fields.integer('Subects Marks',required=True),
              }
    
    _defaults = {
            'subject_marks': 100,
            'exam_offered': _get_exam_offered,
           }
    
    def exam_datesheet(self, cr, uid, ids, context=None):
        print "context: ", context
        for current_obj in self.browse(cr, uid, ids, context=context):
            current_obj
            start_date = current_obj.exam_offered.start_date.split('-')
            datesheet_obj = self.pool.get('sms.exam.datesheet')
            datesheelines_obj = self.pool.get('sms.exam.datesheet.lines')
            
            year = int(start_date[0])
            month = int(start_date[1])
    
            first_date = datetime.date(year, month, 1)
            if month == 12:
                last_date = datetime.date(year + 1, month, 1) - datetime.timedelta(1,0,0)
            else:
                last_date = datetime.date(year, month + 1, 1) - datetime.timedelta(1,0,0)
                
            is_exist_sql = """SELECT sms_exam_datesheet.id FROM sms_exam_datesheet
                 WHERE sms_exam_datesheet.academiccalendar = """ + str(current_obj.academiccalendar.id) + """
                 AND sms_exam_datesheet.exam_type = """ + str(current_obj.exam_offered.exam_type.id) + """
                 AND sms_exam_datesheet.start_date between '""" + str(first_date) + """' AND '""" + str(last_date) + """'"""
                 
            cr.execute(is_exist_sql)
            is_exit_row = cr.fetchone()
            
            if is_exit_row:
                datesheet_id = is_exit_row[0]
            else:
                datesheet_id = datesheet_obj.create(cr,uid,{'academiccalendar':current_obj.academiccalendar.id, 'exam_type':current_obj.exam_offered.exam_type.id,'exam_offered':current_obj.exam_offered.id,'start_date':current_obj.exam_offered.start_date,'status':'Active'})
            
            sql = """SELECT sms_academiccalendar_subjects.id FROM sms_academiccalendar_subjects
                     WHERE sms_academiccalendar_subjects.academic_calendar ="""+str(current_obj.academiccalendar.id)+"""
                     AND sms_academiccalendar_subjects.state = 'Current'"""
            
            cr.execute(sql)
            rec = cr.fetchall()
            
            for each in rec:
                lines_ids = datesheelines_obj.search(cr,uid,[('name','=',datesheet_id),('subject','=',each[0])])
                if not lines_ids:
                    datesheelines_obj.create(cr,uid,
                    {
                    'name':datesheet_id,
                    'subject':each[0],
                    'total_marks':current_obj.subject_marks,
                    'paper_date':datetime.date.today(),
                    'invigilator':1,
                    })
        
exam_datesheet()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: