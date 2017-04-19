import datetime
import pandas
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.backends.backend_pdf import PdfPages
from sqlalchemy import create_engine
import time
import os
import requests
#top_users random 10 :) graph increment problem
#top_users all 10 --emoji :) second graph increments by int 5
#top_users random --emoji :( Default index is stuck at 3. Should change to 10
#top_users random 10 --emoji :)

#TODO: Change all to slack-wide in code
#TODO: Change default behavior for no channel to be slack-wide
engine = create_engine('mysql://{}:{}@{}'.format(os.environ["DB_USERNAME"], os.environ["DB_PASSWORD"], os.environ["DB_CONNECTION_STRING"]), echo=False)

def stats(response, args):
    if args[0] == 'time':
        if len(args)!=4:
            return ["ERROR: Please use the following syntax `time <channel> 2/1/17 5/1/18`"]
        return generate_time_graph(args[2::], args[1])

    if args[0] == 'top_users':
        emoji_stats = False
        channel = args[1]
        index = 10
        if len(args)>4:
            return ["ERROR: Please use the following syntax `top_users <channel> <index> (--emoji)`"]
        try:
            index = int(args[2])
            if args[-1] == "--emoji":
                emoji_stats = True
        except ValueError:
            if args[2] == "--emoji":
                emoji_stats = True
            else:
                return ["ERROR: Please use the following syntax `top_users <channel> <index> (--emoji)`"]
        return collect_top_users(index, channel, emoji_stats)

        pass

    if args[0] == 'emoji':
        pass

    if args[0] == 'channel':
        pass

    if args[0] == 'help':
        return ["""*List of arguments for Stats*
```
time (!stats time random 12/01/15 5/01/17)
    -- Returns time related data on the channel specified, if none given
    then default is slack-wide.
    -- Takes 3 arguments: <channel> <begin date> <end date>

top_users (!stats top_users random, !stats top_users random 10 --emoji)
    -- Returns the top commenters of a given channel. `slack-wide` as channel returns
    slack wide top commenters.
    -- Optional parameter index specifies how many top users to return.
    -- Optional flag `--emoji` will return top users for emoji statistics
    -- Takes max of 3 arguments: <channel> <index> (--emoji
```
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
    if get_emoji_stats == True:
        if channel == 'all':
            top_given = engine.execute("""SELECT u.first_name, u.last_name, SUM(ea.given_count) totalReceived 
                FROM emojiActivity ea 
                JOIN users u 
                ON ea.to_user_id = u.slack_id 
                GROUP BY u.first_name, u.last_name 
                ORDER BY totalReceived ASC limit %s""", 
                index).fetchall()
            top_received = engine.execute("""SELECT u.first_name, u.last_name, SUM(ea.given_count) totalGiven 
                FROM emojiActivity ea 
                JOIN users u 
                ON ea.from_user_id = u.slack_id  
                GROUP BY u.first_name, u.last_name 
                ORDER BY totalGiven ASC limit %s""", 
                index).fetchall()

        else:
            top_received = engine.execute("""SELECT u.first_name, u.last_name, SUM(ea.given_count) totalGiven 
                FROM emojiActivity ea 
                JOIN users u 
                ON ea.from_user_id = u.slack_id 
                WHERE ea.in_channel_id = (
                    SELECT slack_id 
                    FROM channels 
                    WHERE name = %s) 
                GROUP BY u.first_name, u.last_name 
                ORDER BY totalGiven ASC limit %s""", 
                channel, index).fetchall()

            top_given = engine.execute("""SELECT u.first_name, u.last_name, SUM(ea.given_count) totalReceived 
                FROM emojiActivity ea 
                JOIN users u 
                ON ea.to_user_id = u.slack_id 
                WHERE ea.in_channel_id = (
                    SELECT slack_id 
                    FROM channels 
                    WHERE name = %s) 
                GROUP BY u.first_name, u.last_name 
                ORDER BY totalReceived ASC limit %s""", 
                channel, index).fetchall()

        received_names = [x[0]+" "+x[1] for x in top_given]
        received_scores = [int(x[2]) for x in top_given]
        giver_names = [x[0]+" "+x[1] for x in top_received]
        giver_scores = [int(x[2]) for x in top_received]

        giver_df = pandas.DataFrame({'Top Givers':giver_names, 'Score':giver_scores})
        received_df = pandas.DataFrame({'Top Receivers':received_names, "Score":received_scores})
        filepath = '/tmp/'
        file_name = 'Emoji_Bar_Graph_'+channel+'_'+time.strftime('%m-%d-%Y')+'.pdf'

        with PdfPages(filepath+file_name) as pdf:

            giver_bar_graph = giver_df.plot(x='Top Givers', y='Score', kind='barh', legend=False, title='Emoji Givers')
            giver_bar_graph.set_xlabel('Users')
            giver_bar_graph.set_ylabel('Score')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

            received_bar_graph = received_df.plot(x='Top Receivers', y='Score', kind='barh', legend=False, title='Emoji Earners')
            received_bar_graph.set_xlabel('Users')
            received_bar_graph.set_ylabel('Score')
            plt.tight_layout()
            pdf.savefig()
            plt.close()

        upload_to_slack(filepath+file_name, file_name, 'pdf')

    else:
        top_users = engine.execute("""SELECT first_name, last_name, topCommenters.comment_count 
            FROM (
                SELECT from_user_id, comment_count 
                FROM commentActivity 
                WHERE to_channel_id = (
                    SELECT slack_id 
                    FROM channels 
                    WHERE name = %s)) as topCommenters 
            LEFT JOIN users 
            ON topCommenters.from_user_id = users.slack_id 
            ORDER BY comment_count ASC LIMIT %s""", 
            channel, index).fetchall()

        top_users_names = [x[0]+" "+x[1] for x in top_users]
        top_users_scores = [x[2] for x in top_users]

        filepath = '/tmp/'
        file_name = 'Top_Commenters_Bar_Graph_'+channel+'_'+time.strftime('%m-%d-%Y')+'.pdf'

        top_users_df = pandas.DataFrame({'Top Commenters':top_users_names, 'Score':top_users_scores})
        top_users_bar_graph = top_users_df.plot(x='Top Commenters', y='Score', kind='barh', legend=False, title='Top Commenters for '+channel)
        top_users_bar_graph.set_xlabel('Total comments made')
        top_users_bar_graph.set_ylabel('Users')
        plt.tight_layout()
        plt.savefig(filepath+file_name)

        upload_to_slack(filepath+file_name, file_name, 'pdf')

def upload_to_slack(filepath, file_name, file_type):
    print 'PantherBot:LOG:Beginning file upload to Slack'
    my_file = {'file' : (file_name, open(filepath, 'rb'), file_type)}
    payload={
              "filename": file_name, 
              "token":"xoxp-112432628209-170519375364-170581262869-d9c68a368b1865babe1b09ea8d6ca309", 
              "channels":['#random'], 
            }
    resp = requests.post("https://slack.com/api/files.upload", params=payload, files=my_file)
    if resp.json()['ok'] == False:
        print 'PantherBot:LOG:Upload Failed'
    else:
        print 'PantherBot:LOG:Upload Success'

