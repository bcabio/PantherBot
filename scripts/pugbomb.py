#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Created by Harsha Goli
import praw
#from ../bot.py import pug_urls
#pug bombs the chat and destroys this poor bot's soul
def pugbomb(response, args):
    print'deploying pugbomb'

    #gets the number
    #num = [int(s) for s in response["text"].split() if s.isdigit()]
    num = int(args[0])
    if num > 15:
    	num = 15

    payload=[u for u in pug_urls[-15:]]

    return payload

def callingallpugs():
    print 'callingallpugs'
    reddit = praw.Reddit(client_id='aGpQJujCarDHWA',
                     		client_secret='fkA9lp0NDx23B_qdFezTeGyGKu8',
                     		user_agent='my user agent',
                        	password='PHGSU2017',
                        	username='Panther_Bot')

    for submission in reddit.subreddit('pugs').hot(limit=100):
        pug_urls.append(submission.url)

    return pug_urls
