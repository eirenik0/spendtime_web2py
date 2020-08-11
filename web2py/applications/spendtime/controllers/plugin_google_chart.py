
from datetime import datetime

def plugin_google_chart():
    """used with the .load view to create a google chart
    Because this is used in a view LOAD, parameters are passed back from the browser as vars in the URL
    The complulsory vars include: 'type', a string defining the chart_type
        'data_url', which is a URL of the function which returns the data to be charted

    The use in the view is like this (including an example data URL

    {{ data_url = URL('plugin_google_chart','plugin_return_data.json',user_signature=True)}}
    ...
    {{=LOAD('plugin_google_chart','plugin_google_chart.load',ajax=True,
        user_signature=True,vars={'type':'bar','data_url':data_url})}}
    """
    chart_type = request.vars.type
    data_url = request.vars.data_url
    if chart_type and data_url:
        options_dict = request.vars.options_dict or ''
        return dict(chart_type=chart_type,data_url=data_url,
                    options_dict=options_dict)
    else:
        return dict()


def plugin_return_data():
    """ This is an example function to return a JSON-encoded array to the Google chart plugin.
    The URL should have a .json suffix
    This can also use the @auth.requires_signature() decorator
    """
    user_id = auth.user_id
    data=None
    if request.vars.social_type=='vk':
        timeline_table = db(db.timeline.user_extra_id==auth.user_id).select()
        social_type = db(db.user_extra.id==db.timeline.user_extra_id).select()[0]['user_extra']['social_type']
        # add field if end_time not empty
        data = [[t['week_day'], t['start_time'], t['end_time']]
                for t in timeline_table
                if t['end_time'] and social_type=='vk']
    elif request.vars.social_type=='fb':
        timeline_table = db(db.timeline.user_extra_id==auth.user_id).select()
        social_type = db(db.user_extra.id==db.timeline.user_extra_id).select()[0]['user_extra']['social_type']
        # add field if end_time not empty
        data = [[t['week_day'], t['start_time'], t['end_time']] for t in timeline_table if t['end_time'] and social_type=='fb']
    # data =[[T('Sunday ')+'9 '+T('May'),'2014-05-20T02:59:34.349379','2014-05-20T03:00:37.337916'],
    #        ['Monday 6 April','2014-05-20T03:00:45.337916','2014-05-20T04:00:37.337916']]
    if not data: request['data']=None
    return dict(data=data)

