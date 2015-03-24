from openerp.osv import fields, osv

class sms_student_exam_progress_report_single(osv.osv_memory):

    def _get_student(self, cr, uid, ids):
        stdobj = self.browse(cr, uid, ids['active_id'])
        std_id =  stdobj.id
        return std_id

    _name = "sms.student.exam.progress.report.single"
    _description = "Student DMC"
    _columns = {
                'report_type': fields.selection([('Single_Report','Single Report'),('Multiple_Report','Multiple Report')],'Select', required=True, readonly=True),
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True,),
                'student_id': fields.many2one('sms.student','Select Student', readonly=True),
              }
    _defaults = {
            'report_type': 'Single_Report',
            'student_id': _get_student,
       }
    
    def onchange_academiccalendar(self, cr, uid, ids, academiccalendar_id, context=None):
        result = {}
        students = []

        if not academiccalendar_id:
            return {'domain':{'student_id':[('id','in',[])]}, 'value': result}
        
        sql = """SELECT sms_student.id FROM sms_student 
            inner join sms_academiccalendar_student
            ON 
            sms_student.id = sms_academiccalendar_student.std_id
            WHERE sms_academiccalendar_student.name = """ + str(academiccalendar_id)
                
        cr.execute(sql)
        student_ids= cr.fetchall()
        for student in student_ids:
            students.append(student[0])

        return {'domain':{'student_id':[('id','in',students)]}, 'value': result}
     
    def print_dmc(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        
        for obj in current_obj:           
            report = 'sms.student.dmc.multiple.name'
                
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'sms.student.exam.progress.report.single',
            'form': self.read(cr, uid, ids)[0],}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,}
    
sms_student_exam_progress_report_single()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: