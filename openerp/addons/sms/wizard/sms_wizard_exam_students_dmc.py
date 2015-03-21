from openerp.osv import fields, osv

class sms_student_exam_dmc(osv.osv_memory):

    _name = "sms.student.exam.dmc"
    _description = "Student DMC"
    _columns = {
                'dmc_type': fields.selection([('Single_DMC','Single DMC'),('Multiple_DMC','Multiple DMC')],'Select', required=True,),
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True,),
                'student_id': fields.many2one('sms.student','Select Student',),
                'exam_type': fields.many2one('sms.exam.datesheet','Exam Type', required=True, domain="[('academiccalendar','=',academiccalendar_id)]"),
              }
    _defaults = {
            'dmc_type': 'Multiple_DMC',
           }
    
     
    def onchange_academiccalendar(self, cr, uid, ids, academiccalendar_id, context=None):
        result = {}
        students = []
        result['student_id'] = None
        result['exam_type'] = None
        
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
            user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
            if user.company_id.default_dmc_format == 'format1':
                report = 'sms.student.dmc.name'
            elif user.company_id.default_dmc_format == 'format2':
                report = 'sms.student.dmc_formate2.name'
            else:
                raise osv.except_osv(('DMC Format not defined'),('Go to Examination section in Company Setting and define a DMC format.'))
                
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'sms.student.exam.dmc',
            'form': self.read(cr, uid, ids)[0],}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,}
    
sms_student_exam_dmc()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: