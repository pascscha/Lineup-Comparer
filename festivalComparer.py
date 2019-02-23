import requests
import urllib
from bs4 import BeautifulSoup
import re
import codecs
import operator
import sys


def get_soup(url):
    """Return a beautiful soup object from an url"""
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()
    return BeautifulSoup(mystr, 'lxml')


def get_festival_urls(query):
    """returns all festival urls that mach a given query"""
    # perform query
    url = "https://www.electronic-festivals.com"
    f = {"title": query}
    soup = get_soup(url + "/home/result?" + urllib.parse.urlencode(f))

    # get all query results
    events = soup.findAll("div", {"typeof": "http://schema.org/Festival"})

    # put results into array and return them
    out = []
    for event in events:
        out.append(url + event['about'])
    return out

#


def get_acts(url):
    """Return a list of acts for a valid festival url"""
    # open page
    soup = get_soup(url)
    acts = soup.findAll("a", {"data-rank": re.compile(r'.*')})

    # return list of acts and their rating
    out = []
    for act in acts:
        out.append([act.text, int(act["data-rank"])])
    return out


def get_csv(festivals):
    """Returns a csv string comparing all festivals"""
    # Load acts for each festival
    acts = {}
    for festival in festivals:
        festival_urls = get_festival_urls(festival)
        if len(festival_urls) == 0:
            print("Didn't find any results for {}".format(festival))
        else:
            if len(festival_urls) > 1:
                print("Ambiguity for {}, I'm choosing the first one".format(festival))
            acts[festival] = get_acts(festival_urls[0])

    # combine all acts that appear in any of our festivals
    combined = []
    csv = "Act,Rank"
    for f, a in acts.items():
        csv += "," + f
        for i in range(len(a)):
            if not a[i] in combined:
                combined.append(a[i])

    # sort combined acts by their rating
    combined = sorted(combined, key=operator.itemgetter(1))

    # add acts to csv string
    for act in combined:
        csv += "\n{},{}".format(act[0], act[1])
        for f, a in acts.items():
            if act in a:
                csv += ",x"
            else:
                csv += ","
    return csv


if __name__ == "__main__":

    # load default festivals if no arguments were passed
    if len(sys.argv) == 1:
        festivals = ["airbeat one", "electric love", "balaton sound", "world club dome", "ultra music festival - europe"]
    else:
        festivals = sys.argv[1:]

    csv_string = get_csv(festivals)

    # save comparison to file
    with codecs.open("comparison.csv", "w+", "utf-16") as f:
        f.write(csv_string)
