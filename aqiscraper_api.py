"""
The last aqi-scraper used a spoofed user agent to get aqi data. This time I want to try using aqicn's API.
This is in a less gray area, and also should have the advantage of not being at the whims of the developer's
HTML fancies.
"""

import requests
import ast
from keys import *  # This is where I keep my own token to access WAQI's API.


# response = requests.get("https://api.waqi.info/feed/toronto/?token=")
# response_text = response.text
# print(response_text)
# response_dict = ast.literal_eval(response_text)
# aqi = response_dict["data"]["aqi"]
# print(aqi)

def aqi_getter(city: str) -> str:
    """
    This function takes in the city whose AQI you want, and feeds it into the URL for WAQI's API.
    We then GET the url, convert it from a response into a string, convert that to a dictionary, and then
    use dictionary to get it. I found a bug that the WAQI's API doesn't always return the most current AQI,
    so this function also outputs what date and time the AQI is accurate to. Also credits WAQI, and gives
    its sources.
    """
    aqi_url = "https://api.waqi.info/feed/{}/?token={}".format(city, token)
    response = requests.get(aqi_url)
    response_text = response.text  # WAQI returns string, formatted like a dictionary
    response_dict = ast.literal_eval(response_text)  # Turns the string into a dictionary
    aqi = response_dict["data"]["aqi"]
    date_accurate = response_dict["data"]["time"]["s"]
    sourcelist = []
    for attribution in response_dict["data"]["attributions"]:
        sourcelist.append(attribution["name"])
    sources = ", ".join(sourcelist)
    output = "The AQI in {} is {}, accurate to {}. \n \n Data sourced from WAQI, which sourced " \
             "it's data from: {}.".format(city, aqi, date_accurate, sources)
    return output

# print(aqi_getter('ottawa'))


def aqi_getter_console():
    """
    Function to test the AQI getter, in the console
    """

    city = input("Please enter the city whose AQI you would like to see: \n")
    print(aqi_getter(city))

if __name__ == "__main__":
    aqi_getter_console()
