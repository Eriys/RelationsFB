import requests
import json
import base64
import argparse
import random
from localuseragent import ua
import csv

def settings():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", help="Facebook UserID Account", required=True)
    args = parser.parse_args()
    userid = args.id

    typeoflinks = int(input("1 for friends, 2 for followers, 3 for followings, 4 for hometown, 5 for current city, 6 for recent friendship, 7 for friend of high school")) -1

    app_collection = ["2","32","33", "125", "124", '1', "54"]
    b64req = "app_collection:"+str(userid)+":2356318349:"+str(app_collection[typeoflinks])

    encodedBytes = base64.b64encode(b64req.encode("utf-8"))
    encodedStr = str(encodedBytes, "utf-8")
    return(encodedStr, userid)


def extractfriends(data, friends, cursor):
    cursorplace = len(data['data']['node']['pageItems']['edges'])
    if cursorplace != 0:
        newcursor = data['data']['node']['pageItems']['edges'][cursorplace-1]['cursor']
    else:
        if cursor == 0:
            print("No friends found")
            exit()
        newcursor = cursor
    if newcursor != cursor:
        if len(data['data']['node']['pageItems']['edges']) != 1:
            for edge in data['data']['node']['pageItems']['edges']:
                friends.append({
                    'name' : edge['node']['title']['text'],
                    'userid': edge["node"]['node']['id'],
                    'url_profile' : edge['node']['url'],
                    'picture_profile' : edge['node']['image']['uri'],
                    'informations':edge['node']['image']['uri']
                })
    else:
        if cursor == 0:
            print("No friends found")
            exit()
        newcursor = "end"
    return (friends, newcursor)


def all_list(cursor, encodedStr, headers, friends):

    while cursor != "end":

        payload = {
            "av":'0',
            '__user':'0',
            '__a':'1',
            'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
            'variables': '{"count":8,"cursor":"'+str(cursor)+'",'+'"scale":1,"search":null,"id":"'+str(encodedStr)+'"}',
            'server_timestamps': 'true',
            'doc_id': '5225908510806517',
        }

        response = requests.post('https://www.facebook.com/api/graphql', headers=headers, data=payload)

        data = response.json()
        friends, cursor = extractfriends(data, friends, cursor)

    return(friends)

def show_friends(friends, userid):
    with open(f"{userid}.csv", 'w') as f:
        writer= csv.writer(f)
        writer.writerow(['name', 'userid', 'url_profile', 'picture_profile', 'informations'])
        for friend in friends:
            writer.writerow(friend.values())
            print(friend['name'], friend['userid'])


def main():
    headers = {
        'User-Agent': random.choice(ua["browsers"]["chrome"]),
        'Accept': '*/*',
        'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
        'X-FB-Friendly-Name': 'ProfileCometAppCollectionListRendererPaginationQuery',
        'Origin': 'https://www.facebook.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Site': 'same-origin',
    }

    encodedStr, userid = settings()

    data = {
        'av': '0',
        '__user': '0',
        'fb_api_req_friendly_name': 'ProfileCometAppCollectionListRendererPaginationQuery',
        'variables': '{"count":8,"scale":1,"search":null,"id":"'+str(encodedStr)+'"}',
        'server_timestamps': 'true',
        'doc_id': '5225908510806517',
    }

    response = requests.post('https://www.facebook.com/api/graphql/',headers=headers, data=data)
    data = response.json()
    if "errors" in data.keys():
        print("Rate Limit")
        exit()
    if len(data['data']['node']['pageItems']['edges']) == 0:
        print("These profile doesn't exist or doesn't have public friends list profile")
        exit()
    friends = list()

    cursor = ""
    friends, cursor = extractfriends(data, friends, cursor)

    friends = all_list(cursor, encodedStr, headers, friends)
    show_friends(friends, userid)

main()
