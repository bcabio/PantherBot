import datetime
import pandas
from collections import Counter
from sqlalchemy import create_engine
import os
#top_users random 10
#top_users all 10 --emoji
#top_users random --emoji
engine = create_engine('mysql://{}:{}@{}'.format(os.environ["DB_USERNAME"], os.environ["DB_PASSWORD"], os.environ["DB_CONNECTION_STRING"]), echo=False)
def stats(response, args):
    if args[0] == 'time':
        if len(args)!=4:
            return ["ERROR: Please use the following syntax `time <channel> 2/1/17 5/1/18`"]
        return generate_time_graph(args[2::], args[1])

    if args[0] == 'top_users':
        get_emoji_stats = False
        channel = args[1]
        index = 3
        try:
            index = int(args[3])
        except ValueError:
            get_emoji_stats = True

        collect_top_users(index, channel, get_emoji_stats)

        pass

    if args[0] == 'emoji':
        pass

    if args[0] == 'channel':
        pass

    if args[0] == 'help':
        return ["""*List of arguments for Stats*
```
time (g_r time random 12/01/15 5/01/17)
    -- Returns time related data on the channel specified, if none given
    then default is slack-wide.
    -- Takes 3 arguments: <channel> <begin date> <end date>```
        """]

def generate_time_graph(range, channel='all'):
    try:
        date_list = [datetime.datetime.strptime(x, "%m/%d/%y").date() for x in range]
    except ValueError:
        return ["Please input time in the syntax of mm/dd/yy"]
    hour_count = None
    if channel == 'all':
        hour_count = engine.execute("SELECT hour FROM channelActivity WHERE day_of_month >= %s and day_of_month <= %s and month >= %s and month <= %s and year >= %s and year <= %s", date_list[0].day, date_list[1].day, date_list[0].month, date_list[1].month, date_list[0].year, date_list[1].year).fetchall()
    else:
        hour_count = engine.execute("SELECT hour FROM channelActivity WHERE channel_id = (SELECT slack_id FROM channels WHERE name = %s) and day_of_month >= %s and day_of_month <= %s and month >= %s and month <= %s and year >= %s and year <= %s", channel, date_list[0].day, date_list[1].day, date_list[0].month, date_list[1].month, date_list[0].year, date_list[1].year).fetchall()

    counter = Counter()
    for hc in hour_count:
        counter[hc[0]] += 1

    hour=range(0, 24)
    count=[counter[h] for h in hour]

    df = pandas.DataFrame({'Count':count}, index=hour)
    df.columns.name = 'Hour'
    return [str(df)]
 

def collect_top_users(index, channel, get_emoji_stats):
    if get_emoji_stats = False:
        top_users = engine.execute("Select first_name, last_name, topCommenters.comment_count FROM ( SELECT from_user_id, comment_count FROM commentActivity WHERE to_channel_id = %s ) as topCommenters LEFT JOIN users ON topCommenters.from_user_id = users.slack_id ORDER BY comment_count desc limit %s" channel, index)
    
