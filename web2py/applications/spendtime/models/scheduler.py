# -*- coding: utf-8 -*-

# Checking if user online
from datetime import datetime
from urlfetch import fetch
from simplejson import loads

def check_online(type='vk'):
    logger.debug('Check online')
    users = db(db.auth_user).select()   # all registered users
    for user in users:
        # if db(db.user_extra).select(auth_id=auth.user_id):
        #     pass
        if type == 'vk':
            status = loads(fetch(url='https://api.vk.com/method/users.get?user_ids=%s&fields=online'
                                     %user['vk_uid']).content)['response'][0]['online']
            logger.debug("%s %s"%(user['last_name'], status))
            user_exist = db(db.user_extra.auth_id==user['id']).select()  # number of all exist auth_users in user_extra table
            timeline_table = db(db.timeline.user_extra_id==user['id']).select()
            now_time = datetime.now()
            if status and len(user_exist):
                if  not len(timeline_table) or timeline_table[-1]['end_time']:  # if not exist end_time record
                    logger.debug('Insert')
                    db.timeline.insert(week_day=now_time.strftime('%A %d %b'),
                                       user_extra_id=user['id'],
                                       start_time=now_time.isoformat())
                    db.commit()
                else:
                    continue
            elif len(user_exist):
                if (len(timeline_table) and
                        timeline_table[-1]['start_time'] and
                        not timeline_table[-1]['end_time']):
                    logger.debug('Update')
                    timeline_table[-1].end_time=now_time.isoformat()
                    timeline_table[-1].update_record()
        elif type == 'facebook':
            pass

    return True or False

# def write_to_db():
#     if check_online(user_id):
from gluon.scheduler import Scheduler
scheduler = Scheduler(db)

# scheduler.queue_task(task_add,pvars=dict(a=1,b=2))
scheduler.queue_task(check_online())