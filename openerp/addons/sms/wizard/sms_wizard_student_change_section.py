from openerp.osv import fields, osv
import datetime

class student_change_section(osv.osv_memory):

    _name = "student.change.section"
    _description = "Student Change Section"
    _columns = {
                'academiccalendar_id': fields.many2one('sms.academiccalendar','From Class', domain="[('state','=','Active')]", required=True),
                'academiccalendar_to_id': fields.many2one('sms.academiccalendar','To Class',  required=True),
              }
    _defaults = {
           }
    
    def onchange_academiccalendar(self, cr, uid, ids, academiccalendar_id, context=None):
        result = {}
        current_obj = self.pool.get('sms.academiccalendar').browse(cr, uid, academiccalendar_id, context=context)
        class_id = current_obj.class_id.id
        academiccalendar_ids = self.pool.get('sms.academiccalendar').search(cr,uid,[('id','!=',current_obj.id),('class_id','=',class_id),('state','=','Active')])
        res = {'domain': {'academiccalendar_to_id': [('id', 'in', academiccalendar_ids),('state','=','Active'),]}}
        return res 
        
    def student_change_section(self, cr, uid, ids, context=None):
        current_obj = self.browse(cr, uid, ids, context=context)
        
        cr.execute("""select id,name from ir_ui_view 
                    where model= 'sms.student.change.section' 
                    and type='tree'""")
        view_res = cr.fetchone()
            
        sql="""delete from sms_student_change_section"""
        cr.execute(sql)
        cr.commit()

        sql = """SELECT sms_student.id, sms_student.registration_no, sms_student.name, sms_student.father_name, sms_academiccalendar_student.id
            from sms_student 
            inner join sms_academiccalendar_student
            on sms_student.id = sms_academiccalendar_student.std_id
            where sms_academiccalendar_student.name = """ + str(current_obj[0].academiccalendar_id.id) + """
            and sms_academiccalendar_student.state = 'Current'
            and sms_student.state = 'Admitted'
            ORDER BY name, father_name"""
        
        cr.execute(sql)
        student_rows = cr.fetchall()
        for student_row in student_rows:            
            sms_temp_detail_new_id = self.pool.get('sms.student.change.section').create(cr,uid,
            {
                'student':student_row[0],
                'registration_no':student_row[1],
                'name':student_row[2],
                'father_name':student_row[3],
                'sms_academiccalendar_student':student_row[4],
                'sms_academiccalendar_from':current_obj[0].academiccalendar_id.id,
                'sms_academiccalendar_to':current_obj[0].academiccalendar_to_id.id,
                'change_section':False,})
                 
        return {
            #'domain': "[('parent_default_exam','=',"+str(sms_temp_new_id)+")]",
            'name': 'Change Student Section: ' +  str(current_obj[0].academiccalendar_id.name),
            'view_type': 'form',
            'view_mode': 'tree',
            'res_model': 'sms.student.change.section',
            'view_id': view_res,
            'type': 'ir.actions.act_window'}
        
student_change_section()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: