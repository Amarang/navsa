import bs4, urllib2, datetime
import config
from dateutil.parser import parse


def getPapers(category):
    data = urllib2.urlopen("http://export.arxiv.org/api/query?search_query=cat:%s&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending" % category).read()

    # data = open("arxivapi.txt").read()

    bs = bs4.BeautifulSoup(data)

    recentpapers = []
    papers = []
    for entry in bs.find_all('entry'):
        title = entry.title.text.replace("\n","").replace("  "," ")
        published = entry.published.text
        date = parse(published).replace(tzinfo=None)
        time = "%d/%d/%d" % (date.month, date.day, date.year)
        now = datetime.datetime.now().replace(tzinfo=None)

        pdfurl = ""
        for link in entry.find_all('link'):
            # print link
            # print link.keys
            if link.has_attr('title'):
                pdfurl = link['href']
        # print now-date
        if( (now-date).days < 2):

            recentpapers.append( [ title, pdfurl, time ] )

        papers.append( [ title, pdfurl, time ] )


        # date -= datetime.timedelta(hours=7) # GMT to Pacific (DST?!)
        # print date


    return recentpapers, papers


def getArxiv():
    output = ""
    outputDetail = ""

    recentpapers1, papers1 = getPapers(config.arxiv['field1'])
    recentpapers2, papers2 = getPapers(config.arxiv['field2'])
    recentpapers = recentpapers1 + recentpapers2
    papers = papers1 + papers2
    print "got papers"

    if(len(recentpapers) > 0):
        output += "Check out the arXiv:"
    output += "<ul>"
    outputDetail += "Recent arXiv papers:<ul>"

    for paper in recentpapers:
        title, pdfurl, time = paper
        output += "<li>%s (%s)</li>" % (title, pdfurl)
    output += "</ul>"

    for paper in papers:
        title, pdfurl, time = paper
        outputDetail += "<li>[%s] %s (%s)</li>" % (time, title, pdfurl)
    outputDetail += "</ul>"



    # print recentpapers, papers

    return output, outputDetail


if __name__=='__main__':
    print getArxiv()
