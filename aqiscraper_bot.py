"""
Goal: Build a reddit bot that returns the AQI of any city, when the bot is called. Uses praw and Reddit's API.

Stretch:
Add feature so instead of the city having to be the second word in the comment, as long as the city is after the
username mention, it will work.

Add feature to schedule the bot to run after a e\certain time interval.

Problem: Cities with multiple words (i.e. San Francisco, New Delhi.) Need to take care of spaces.

Challenges:
-How to scrape AQI
-How to connect to Reddit
(solved using PRAW)
-How to figure out which comments are to be replied to
(solved by cross referencing messages that mention with unread messages)
-How to schedule it to run continuosly
(solved using schedule module)
-What to do in case there's an invalid input
-How to parse the comment for legible city names, especially for cities made up of multiple words

Inputs it works for:
- A comment of form "<random stuff> /u/aqi-bot '<city name>' <random stuff>" (<city name> can be multiple words, must be
in quotes).

Exceptions it can handle:
-"<random> /u/aqi-bot <not a city name> <random>
-"<random> /u/aqi-bot" (No input)

"""
import praw
import schedule
from aqiscraper_api import aqi_getter
import time

reddit = praw.Reddit('bot1',
                     user_agent='Windows:aqi-bot:v0 (by /u/aqi-bot)')


def comment_after(comment, target):
    """
    Finds where /u/aqi-bot is mentioned in the comment, and then figures out the city from there.
    The parameter comment is a list, the parsed version of the comment used in the main program.
    Because many cities have multiple words (i.e. New Delhi, San Francisco), instead of just returning
    the word that comes after the mention of /u/aqi-bot, this function insteads first checks if the
    word following the mention contains a quote, and then looks for the second quote in the following words,
    adding any words in between to the city name.
    """
    charset = ["'", '"']
    targetindex = comment.index(target)
    count = 0
    track = 0
    indextracker = targetindex + 1
    cityname = []
    for char in comment[indextracker]:  # This loop checks if the first word after the mention has a quote.
        if char in charset:
            track += 1
    if track > 0:
        cityname.append(comment[indextracker])
    if track == 1:  # This loop looks for the closing quote, if the word only has one,
                    # adding words in between to the city name.
        indextracker += 1
        while indextracker < len(comment) and count < 1:
            cityname.append(comment[indextracker])
            for char in comment[indextracker]:
                if char in charset:
                    count += 1
            indextracker += 1
    return " ".join(cityname) if len(cityname) > 0 else None


print(comment_after(['/u/aqi-bot', '"Shanghai"'], '/u/aqi-bot'))


def aqi_bot_run():
    """
    Created a function to run the aqi-bot, so that I can feed it into a scheduling API more easily.
    """
    mentionidlist = []  # To keep track of mentions
    for mention in reddit.inbox.mentions(limit=25):
        mentionidlist.append(mention.id)
        # mention.mark_unread() #Get rid of this when done testing.

    for unread in reddit.inbox.unread(limit=25):
        unread.mark_read()  # So it won't parse over it again.
        if unread.id in mentionidlist:  # Check if the unread messages contain something that mentions me
            parsedunread = unread.body.split(" ")
            # print(parsedunread)
            if len(parsedunread) >= 2:
                try:
                    city = comment_after(parsedunread, "/u/aqi-bot")
                    city = city[1:-1]
                    city.replace(" ", "%20")  # Replace spaces with this character, which is what WAQI uses.
                    aqi_text = aqi_getter(city)
                    unread.reply(aqi_text)
                except (KeyError, TypeError, IndexError):
                    # print("My bad")
                    unread.reply("Sorry, but I was unable to find the AQI data for the given input."
                                 "\n \n Note that the input format for aqi-bot is: /u/aqi-bot '<city>'. ")


schedule.every(3).minutes.do(aqi_bot_run)

while True:
    schedule.run_pending()
    time.sleep(20)
