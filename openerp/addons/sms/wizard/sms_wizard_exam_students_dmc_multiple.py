from openerp.osv import fields, osv

class sms_student_exam_dmc_multiple(osv.osv_memory):

    _name = "sms.student.exam.dmc.multiple"
    _description = "Student DMC"
    _columns = {
                'report_type': fields.selection([('Single_Report','Single Report'),('Multiple_Report','Multiple Report')],'Select', required=True,),
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True,),
                'student_id': fields.many2one('sms.student','Select Student',),
#                'exam_type': fields.many2many('sms.exam.datesheet','sms_wizard_exam_datesheet_exam_type_rel','exam_wizard_id','exam_type','Exam Types', required=True, domain="[('academiccalendar','=',academiccalendar_id)]"),
              }
    _defaults = {
            'report_type': 'Multiple_Report',
           }
    
     
    def onchange_academiccalendar(self, cr, uid, ids, academiccalendar_id, context=None):
        result = {}
        result['student_id'] = None
        result['exam_type'] = None
        sql = """SELECT sms_student.id FROM sms_student 
            inner join sms_academiccalendar_student
            ON 
            sms_student.id = sms_academiccalendar_student.std_id
            WHERE sms_academiccalendar_student.name = """ + str(academiccalendar_id)
                
        cr.execute(sql)
        student_ids= cr.fetchall()
        
        return {'domain':{'student_id':[('id','in',student_ids)]}, 'value': result}

    def print_dmc(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        
        for obj in current_obj:           
            report = 'sms.student.dmc.multiple.name'
                
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'sms.student.exam.dmc.multiple',
            'form': self.read(cr, uid, ids)[0],}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,}
    
sms_student_exam_dmc_multiple()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: