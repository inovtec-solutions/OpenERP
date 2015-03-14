from openerp.osv import fields, osv

class move_swap_timetable(osv.osv_memory):

    def _get_day(self, cr, uid, context={}):
        day_id = self.pool.get('sms.day').search(cr, uid, [('name','=','Monday')])
        return day_id[0]
    
    _name = "move.swap.timetable"
    _description = "Swap or Move Timetable"
    _columns = {
                'move_swap_type': fields.selection([('Move_All','Move All'),('Swap_All','Swap All'),('Move_Single','Move Single Day'),('Swap_Single','Swap Single Day')],'Select', required=True,),
                'day': fields.many2one('sms.day', 'Select Day', domain="[('active','=','Active')]"),
                'timetable': fields.many2one('sms.timetable', 'Select Timetable', domain="[('state','in',['Draft','Active'])]", required=True),
                'timetable_from': fields.many2one('sms.timetable.lines', 'Select Entry 1', domain="[('type','=','Period'),('timetable_id','=',timetable),('day_id','=',day)]]", required=True),
                'timetable_with': fields.many2one('sms.timetable.lines', 'Select Entry 2', domain="[('type','=','Period'),('timetable_id','=',timetable),('id','!=',timetable_from),('day_id','=',day)]]"),
                'timetable_slot': fields.many2one('sms.timetable.slot', 'Select Slot'),
                'period_no': fields.integer('Period No', required=True),
             }
    _defaults = {
            'move_swap_type': 'Swap_All',
            'day': _get_day,
           }

    def move_swap_timetable(self, cr, uid, ids, context=None):
        result = []
        for datas in self.browse(cr, uid, ids, context=context):
            if datas.move_swap_type == 'Move_Single' or datas.move_swap_type == 'Move_All':
                teacher_id = datas.timetable_from.teacher_id
                slot_name = datas.timetable_slot.name
                day_id = datas.timetable_from.day_id.id
                
                ############### CHECK IF Slot is EMPTY THEN MOVE IS POSSIBLE 
                is_clash = True
                if datas.move_swap_type == 'Move_Single':
                    is_clash = self.check_clash(cr, uid, teacher_id, slot_name, day_id, context)
                    if is_clash:                
                        raise osv.except_osv('Clash .....', "You cannot move record due to clash. ")
                    else:
                        self.pool.get('sms.timetable.lines').write(cr, uid, datas.timetable_from.id, {'timetable_slot_id': datas.timetable_slot.id, 'period_break_no':datas.period_no})
            
                else:
                    is_clash = self.check_clash(cr, uid, teacher_id, slot_name, None, context)
                    if is_clash:                
                        raise osv.except_osv('Clash .....', "You cannot move record due to clash. ")
                    else:
                        lines_ids = self.pool.get('sms.timetable.lines').search(cr, uid, [('timetable_id','=',datas.timetable_from.timetable_id.id),('teacher_id','=',datas.timetable_from.teacher_id.id),('timetable_slot_id','=',datas.timetable_from.timetable_slot_id.id)])
                        self.pool.get('sms.timetable.lines').write(cr, uid, lines_ids, {'timetable_slot_id': datas.timetable_slot.id, 'period_break_no':datas.period_no})
                
            elif datas.timetable_from.teacher_id.id == datas.timetable_with.teacher_id.id:
                slot_from_id = datas.timetable_from.timetable_slot_id.id
                teacher_from_id =   datas.timetable_from.teacher_id.id
                
                slot_with_id = datas.timetable_with.timetable_slot_id.id
                teacher_with_id = datas.timetable_with.teacher_id.id
                day_id = datas.timetable_from.day_id.id
                if datas.move_swap_type == 'Swap_Single':
                    self.pool.get('sms.timetable.lines').write(cr, uid, datas.timetable_from.id, {'timetable_slot_id': slot_with_id, 'period_break_no':datas.timetable_with.period_break_no})
                    self.pool.get('sms.timetable.lines').write(cr, uid, datas.timetable_with.id, {'timetable_slot_id': slot_from_id, 'period_break_no':datas.timetable_from.period_break_no})
                else:
                    
                    lines_ids_from = self.pool.get('sms.timetable.lines').search(cr, uid, [('timetable_id','=',datas.timetable_from.timetable_id.id),('teacher_id','=',datas.timetable_from.teacher_id.id),('timetable_slot_id','=',datas.timetable_from.timetable_slot_id.id)])
                    lines_ids_with = self.pool.get('sms.timetable.lines').search(cr, uid, [('timetable_id','=',datas.timetable_with.timetable_id.id),('teacher_id','=',datas.timetable_with.teacher_id.id),('timetable_slot_id','=',datas.timetable_with.timetable_slot_id.id)])

                    self.pool.get('sms.timetable.lines').write(cr, uid, lines_ids_from, {'timetable_slot_id': slot_with_id, 'period_break_no':datas.timetable_with.period_break_no})
                    self.pool.get('sms.timetable.lines').write(cr, uid, lines_ids_with, {'timetable_slot_id': slot_from_id, 'period_break_no':datas.timetable_from.period_break_no})
                    
            else:
                slot_from_id = datas.timetable_from.timetable_slot_id.id 
                slot_from = datas.timetable_from.timetable_slot_id.name
                teacher_from_id =   datas.timetable_from.teacher_id.id
                day_id = datas.timetable_from.day_id.id
                
                slot_with_id = datas.timetable_with.timetable_slot_id.id
                slot_with = datas.timetable_with.timetable_slot_id.name
                teacher_with_id = datas.timetable_with.teacher_id.id
                
                if datas.move_swap_type == 'Swap_Single':
                    is_clash_from = self.check_clash(cr, uid, teacher_from_id, slot_with, day_id, context)
                    is_clash_with = self.check_clash(cr, uid, teacher_with_id, slot_from, day_id, context)
                    if is_clash_from or is_clash_with:
                        raise osv.except_osv('Clash .....', "You cannot swap these records. ")
                    else:
                        self.pool.get('sms.timetable.lines').write(cr, uid, datas.timetable_from.id, {'timetable_slot_id': slot_with_id, 'period_break_no':datas.timetable_with.period_break_no})
                        self.pool.get('sms.timetable.lines').write(cr, uid, datas.timetable_with.id, {'timetable_slot_id': slot_from_id, 'period_break_no':datas.timetable_from.period_break_no})
                
                elif datas.move_swap_type == 'Swap_All':
                    is_clash_from = self.check_clash(cr, uid, teacher_from_id, slot_with, None, context)
                    is_clash_with = self.check_clash(cr, uid, teacher_with_id, slot_from, None, context)
                    if is_clash_from or is_clash_with:
                        raise osv.except_osv('Clash .....', "You cannot swap these records. ")
                    else:
                        lines_ids_from = self.pool.get('sms.timetable.lines').search(cr, uid, [('timetable_id','=',datas.timetable_from.timetable_id.id),('teacher_id','=',datas.timetable_from.teacher_id.id),('timetable_slot_id','=',datas.timetable_from.timetable_slot_id.id)])
                        lines_ids_with = self.pool.get('sms.timetable.lines').search(cr, uid, [('timetable_id','=',datas.timetable_with.timetable_id.id),('teacher_id','=',datas.timetable_with.teacher_id.id),('timetable_slot_id','=',datas.timetable_with.timetable_slot_id.id)])
                        
                        self.pool.get('sms.timetable.lines').write(cr, uid, lines_ids_from, {'timetable_slot_id': slot_with_id,  'period_break_no':datas.timetable_with.period_break_no})
                        self.pool.get('sms.timetable.lines').write(cr, uid, lines_ids_with, {'timetable_slot_id': slot_from_id,  'period_break_no':datas.timetable_from.period_break_no})

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

move_swap_timetable()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: