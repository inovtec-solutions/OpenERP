from openerp.osv import fields, osv

class timetable_entry(osv.osv_memory):

    def _get_day(self, cr, uid, context={}):
        day_id = self.pool.get('sms.day').search(cr, uid, [('name','=','Monday')])
        return day_id[0]
    
    _name = "timetable.entry"
    _description = "Timetable Entry"
    _columns = {
                'day_type': fields.selection([('All','All'),('Single_Day','Single Day')],'Select', required=True,),
                'timetable_id': fields.many2one('sms.timetable','Timetable'),
                'period_break_no': fields.integer('Sequence No', required = True),
                'type': fields.selection([('Period', 'Period'),('Break', 'Break')], 'Slot Type', required = True),
                'teacher_id': fields.many2one('hr.employee','Teacher'),
                'subject_id': fields.many2one('sms.academiccalendar.subjects','Subject', domain="[('teacher_id','=',teacher_id),('teacher_id','!=',None)]]"),
                'day_id': fields.many2one('sms.day','Day', required = True),
                'timetable_slot_id': fields.many2one('sms.timetable.slot','Timing', required = True),
                'is_lab': fields.boolean('Is Lab'),    
              }
    _defaults = {
            'day_type': 'All',
            'type': 'Break',
            'day_id': _get_day,
           }

   
        
    def onchange_type(self, cr, uid, ids, type, context=None):
        result = {}
        print "type: ", type
        if type == 'Break':
            result['teacher_id'] = ''
            result['subject_id'] = ''
            return {'value': result}
        return {}
    
    def timetable_entry(self, cr, uid, ids, context=None):
        result = []
        for datas in self.browse(cr, uid, ids, context=context):
            print "datas: ", datas
            if datas.day_type == 'All':
                
                days_ids = self.pool.get('sms.day').search(cr,uid,[('active','=','Active')])
        
                ############### CHECK IF Slot is EMPTY THEN MOVE IS POSSIBLE 
                if datas.type == 'Period':
                    for day_id in days_ids:
                        self.pool.get('sms.timetable.lines').create(cr, uid, {
                            'is_lab': False,
                            'type': datas.type,
                            'period_break_no': datas.period_break_no,
                            'subject_id': datas.subject_id.id,
                            'teacher_id': datas.teacher_id.id,
                            'day_id': day_id,
                            'timetable_slot_id': datas.timetable_slot_id.id,
                            'timetable_id': datas.timetable_id.id,}, context=context)
                     
                else:
                    for day_id in days_ids:
                        self.pool.get('sms.timetable.lines').create(cr, uid, {
                            'type': datas.type,
                            'period_break_no': datas.period_break_no,
                            'day_id': day_id,
                            'timetable_slot_id': datas.timetable_slot_id.id,
                            'timetable_id': datas.timetable_id.id,}, context=context)
            else:
                if datas.type == 'Period':
                    self.pool.get('sms.timetable.lines').create(cr, uid, {
                        'is_lab': False,
                        'type': datas.type,
                        'period_break_no': datas.period_break_no,
                        'subject_id': datas.subject_id.id,
                        'teacher_id': datas.teacher_id.id,
                        'day_id': datas.day_id.id,
                        'timetable_slot_id': datas.timetable_slot_id.id,
                        'timetable_id': datas.timetable_id.id,}, context=context)
                else:
                    self.pool.get('sms.timetable.lines').create(cr, uid, {
                        'type': datas.type,
                        'period_break_no': datas.period_break_no,
                        'day_id': datas.day_id.id,
                        'timetable_slot_id': datas.timetable_slot_id.id,
                        'timetable_id': datas.timetable_id.id,}, context=context)
        
        return result
    
    def check_clash(self, cr, uid, teacher_id, slot_name, day_id, context=None):
        teacher_id = int(teacher_id)
        # "09:15 AM -- 09:45 AM"
        slot_start_time = 0
        slot_end_time = 0
        
        asigned_start_time = 0
        asigned_end_time = 0
        
        start = slot_name.split("--")[0].strip()
        end = slot_name.split("--")[1].strip()
        
        slot_start_time_hour = int(start.split(" ")[0].split(":")[0])
        slot_start_time_min = int(start.split(" ")[0].split(":")[1])
        slot_start_time_am_pm = start.split(" ")[1]
        
        if slot_start_time_am_pm == 'PM' and slot_start_time_hour != 12:
            slot_start_time_hour = slot_start_time_hour + 12
        slot_start_time =  slot_start_time_hour * 60 + slot_start_time_min
        
        slot_end_time_hour = int(end.split(" ")[0].split(":")[0])
        slot_end_time_min = int(end.split(" ")[0].split(":")[1])
        slot_end_time_am_pm = end.split(" ")[1]
        
        if slot_end_time_am_pm == 'PM' and slot_end_time_hour != 12:
            slot_end_time_hour = slot_end_time_hour + 12
        slot_end_time =  slot_end_time_hour * 60 + slot_end_time_min
        
        timetable_lines_ids = ""
        if day_id:
            timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('teacher_id','=',teacher_id),('day_id','=',day_id)])
        else:
            timetable_lines_ids = self.pool.get('sms.timetable.lines').search(cr,uid,[('teacher_id','=',teacher_id)])
        timetable_lines_objs = self.pool.get('sms.timetable.lines').browse(cr, uid, timetable_lines_ids, context=context)
        
        for rec in timetable_lines_objs:
            start_time_hour = rec.timetable_slot_id.start_time.hour
            start_time_min = rec.timetable_slot_id.start_time.minute
            
            if rec.timetable_slot_id.start_time.am_pm == 'PM' and start_time_hour != 12:
                start_time_hour = start_time_hour + 12
                
            end_time_hour = rec.timetable_slot_id.end_time.hour
            end_time_min = rec.timetable_slot_id.end_time.minute
            
            if rec.timetable_slot_id.end_time.am_pm == 'PM' and end_time_hour != 12:
                end_time_hour = end_time_hour + 12
            
            asigned_start_time = start_time_hour * 60 + start_time_min
            asigned_end_time = end_time_hour * 60 + end_time_min
      
            if slot_start_time <= asigned_start_time and slot_end_time >= asigned_end_time: 
                return True
            elif slot_start_time >= asigned_start_time and slot_end_time <= asigned_start_time: 
                return True
                                
        return False

timetable_entry()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: