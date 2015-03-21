from openerp.osv import fields, osv

class sms_student_exam_lists(osv.osv_memory):

    def onchange_exam_type(self, cr, uid, ids, academiccalendar_id, context=None):
        employee_ids = []
        
        sql = """SELECT distinct uid FROM  res_groups 
            inner join res_groups_users_rel on 
            res_groups.id = res_groups_users_rel.gid
            where (res_groups.name = 'Exam Officer' or res_groups.name = 'Exam Manager') 
            AND res_groups_users_rel.uid = """ + str(uid)
        cr.execute(sql)
        if cr.fetchone():
            employee_ids = self.pool.get('hr.employee').search(cr,uid,[])
        else:
            resource_ids = self.pool.get('resource.resource').search(cr,uid,[('user_id','=',uid)])
            employee_ids = self.pool.get('hr.employee').search(cr,uid,[('resource_id','in',resource_ids)])
        
        return {'domain':{'subject_id':[('academic_calendar','=',academiccalendar_id),('teacher_id','in',employee_ids)]}}

    _name = "sms.student.exam.lists"
    _description = "Student Exam List"
    _columns = {
                'list_type': fields.selection([('Signature_Sheet','Signature Sheet'),('Award_List','Award List'),('Result_List','Result List'),('Result_Sheet','Result Sheet')],'Select', required=True,),
                'academiccalendar_id': fields.many2one('sms.academiccalendar','Select Class', domain="[('state','=','Active')]", required=True,),
                'exam_type': fields.many2one('sms.exam.datesheet','Exam Type', required=True, domain="[('academiccalendar','=',academiccalendar_id)]"),
                'subject_id': fields.many2one('sms.academiccalendar.subjects','Subject', domain="[('academic_calendar','=',academiccalendar_id)]",),
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