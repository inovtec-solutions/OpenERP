from openerp.osv import fields, osv

class sms_student_exam_lists(osv.osv_memory):

    _name = "sms.student.exam.lists"
    _description = "Student Exam List"
    _columns = {
                'list_type': fields.selection([('Signature_Sheet','Signature Sheet'),('Award_List','Award List'),('Result_List','Result List'),('Result_Sheet','Result Sheet')],'Select', required=True,),
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True,),
                'subject_id': fields.many2one('sms.academiccalendar.subjects','Subject', domain="[('academic_calendar','=',academiccalendar_id)]",),
                'exam_type': fields.many2one('sms.exam.datesheet','Exam Type', required=True, domain="[('academiccalendar','=',academiccalendar_id)]"),
                'order_by': fields.selection([('sms_student.name','Student Name'), ('marks desc','Marks'), ('percentage desc','Percentage'),('sms_student.gender','Gender')],'Order By', required=True,),
              }
    _defaults = {
            'list_type': 'Signature_Sheet',
            'order_by': 'sms_student.name',
           }
    
     
    def onchange_academiccalendar(self, cr, uid, ids, context=None):
        result = {}
        result['subject_id'] = None
        result['exam_type'] = None
        return {'value': result}
    
    def print_list(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        
        for obj in current_obj:
           
            if obj.list_type == 'Signature_Sheet':
                report = 'sms.student.signature.list.name'
            elif obj.list_type == 'Award_List':
                report = 'sms.student.award.list.name'
            elif obj.list_type == 'Result_List':
                report = 'sms.student.result.list.name'
            elif obj.list_type == 'Result_Sheet':
                report = 'sms.student.result.sheet.name'
            elif obj.list_type == 'Date_Sheet':
                report = 'sms.student.date.sheet.name'
                
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'sms.student.exam.lists',
            'form': self.read(cr, uid, ids)[0],}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,}
    

sms_student_exam_lists()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: