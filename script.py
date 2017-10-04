""" Script to get issues and bugs from jira """

import json
import sys
import os

from urllib.request import urlopen
# ==============================================================================


def request(url):
    """Function to make requirements"""
    response = urlopen(url).read().decode('utf8')
    obj = json.loads(response)
    return obj


def getLink(link, maxi, dic, par, name):
    """Function to get links of issues"""
    start = 0
    while True:
        url = link.format(maxi, start)
        obj = request(url)
        issues = obj["issues"]

        for issue in issues:
            issueUrl = issue["self"]
            dic[par].append(issueUrl)

        if (start >= obj["total"]):
            print("Complete")
            try:
                os.makedirs("./{}".format(par))
            except:
                pass

            with open('{}/{}.json'.format(par, name), 'w') as outfile:
                json.dump(dic, outfile)
            dic = dic[par]
            with open('temp/{}.json'.format(name), 'w') as outfile:
                json.dump(dic, outfile)
            break

        # show script progress in terminal
        percentage = 100 * start // obj["total"]
        percentage = str(percentage) + "%"
        print("{}".format(percentage))
        sys.stdout.write("\033[F")

        start += maxi


def getDetails(par, name):
    """Function to get the details of issues"""

    os.system("git clone https://github.com/spring-projects/spring-framework")
    with open('temp/{}.json'.format(name)) as data_file:
        data = json.load(data_file)

    total = len(allIssueUrl["issues"])
    cont = 0

    for x in data:
        # show script progress in terminal
        total = "{} {} are missing".format(len(data), par)
        print("{}".format(total))
        sys.stdout.write("\033[F")

        filtered = filter(request(x))
        issueId = filtered["issueID"]
        with open('{}/{}.json'.format(par, issueId), 'w') as outfile:
            json.dump(filtered, outfile)
        del data[0]

        with open('temp/{}.json'.format(name), 'w') as outfile:
            json.dump(data, outfile)

        cont += 1


def filter(json):
    dic = {}
    comments = []

    dic["issueID"] = json["id"]
    dic["title"] = json["fields"]["summary"]
    dic["author"] = json["fields"]["creator"]["displayName"]

    dic["reportDate"] = json["fields"]["created"]
    dic["fixDate"] = json["fields"]["resolutiondate"]

    os.system("git -C spring-framework log -1 --before={} > temp/log.log".format(json["fields"]["created"]))

    arq = open('temp/log.log', 'r')
    commit = arq.readlines()

    dic["commitReport"] = {}
    strCommit = str(commit[0]).split()
    dic["commitReport"]["commitReport"] = strCommit[1]

    if ("Author" in str(commit[1])):
        strCommit = str(commit[1]).split(": ")
    else:
        strCommit = str(commit[2]).split(": ")

    strCommit = str(strCommit[1]).split(" <")
    dic["commitReport"]["nameReport"] = strCommit[0]

    strCommit = strCommit[1].split(">")
    dic["commitReport"]["emailReport"] = strCommit[0]

    arq.close()

    dic["labels"] = json["fields"]["issuetype"]["name"]

    dic["description"] = json["fields"]["description"]

    Maxcomments = json["fields"]["comment"]["total"]

    for x in range(Maxcomments):
        comments.append(json["fields"]["comment"]["comments"][x]["body"])
    if (Maxcomments > 0):
        dic["comments"] = comments
    else:
        dic["comments"] = []

    return dic


# ==============================================================================
allIssueUrl = {"issues": []}
allBugsUrl = {"bugs": []}
# ==============================================================================
try:
    os.makedirs("./temp")
except:
    pass

print("Choose an option:\n1: Get issues\n2: Get bugs")
print("3: Get issues details\n4: Get bugs details\n")
choosen = int(input())

if(choosen == 1):
    print("Getting list of issues:")
    url = "https://jira.spring.io/rest/api/2/search?jql=project=SPR+and+resolutiondate!=null&maxResults={}&startAt={}"
    getLink(url, 1000, allIssueUrl, "issues", "issuesUrls")

elif(choosen == 2):
    print("Getting list of bugs:")
    url = "https://jira.spring.io/rest/api/2/search?jql=project=SPR+and+issuetype=Bug+and+resolutiondate!=null&maxResults={}&startAt={}"
    getLink(url, 100, allBugsUrl, "bugs", "bugsUrls")

elif(choosen == 3):
    print("Getting details of issues:")
    getDetails("issues", "issuesUrls")

elif(choosen == 4):
    print("Getting details of issues:")
    getDetails("bugs", "bugsUrls")
