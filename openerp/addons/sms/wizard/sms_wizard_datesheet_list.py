from openerp.osv import fields, osv

class sms_exam_datesheet_list(osv.osv_memory):
    
    def get_exam_offered(self, cr, uid, ids):
        #return {'domain': {'academiccalendar_id': [('id','in', [])]}, 'value': {'exam_offered': ids['active_id']}}
        return ids['active_id']
    
    _name = "sms.exam.datesheet.list"
    _description = "Exam Date Sheet Lists"
    _columns = {
                'exam_offered': fields.many2one('sms.exam.offered','Exam Offered', readonly=True),
                'exam_datesheet': fields.many2one('sms.exam.datesheet','Select Class', domain="[('exam_offered','=',exam_offered)]", help="For Class wise Date Sheet, select specific class"),
                'order_by': fields.selection([('date','Paper Date'),('subject','Subject Name'), ('invigilator','Invigilator')],'Order By', required=True,),
              }
    _defaults = {
            'exam_offered': get_exam_offered,
            'order_by': 'date',
           }
    
    def print_list(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        report = 'sms.student.date.sheet.name'
                
        datas = {
            'ids': [],
            'active_ids': '',
            'model': 'sms.exam.datesheet.list',
            'form': self.read(cr, uid, ids)[0],}
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name':report,
            'datas': datas,}
    

sms_exam_datesheet_list()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: