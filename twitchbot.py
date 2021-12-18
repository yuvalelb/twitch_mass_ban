import requests
import json
from time import sleep


print('welcome to yoyo\'s banning service! here we can ban to your hearts content! please make sure there is a text file called "banlist.txt" in the same folder as '
      'this script! \nit will be checked as soon as you enter your twitch name. \nalso make sure that the ban list looks like this: <name of the user getting banned> '
      '<reason the user is getting banned> in each line, \nif no reason is specified the default reason would be listed as "ban listed", \nbut there has to be exactly '
      'one '
      'username each row')
name= input("please inter your twitch name\n")
try:
    f = open('banlist.txt', 'r')
except:
    print("can't open the file, make sure it's called banlist.txt")
    exit(1)
else:
    print('banlist.txt was opened successfully')

client_id = 'help'
while client_id.lower() == 'help' :
    client_id = input('please inter your client id! if you\'re not sure how to get one enter "help"\n')
    if client_id.lower() == 'help':
        print("to get your client id and access id (will be used later) you can go to https://twitchtokengenerator.com/ go down to the 'available token scopes and "
              "check the moderator:manage:banned_users scope to enable user banning via an application (specifically this application) and then click on the "
              "'generate token!' botton in green at the end of the list, it'll then take you to the tokens it generated, for this application we'll need the "
              "'access token and the client id, in this case you'll need to copy the client id and paste it here")
    else:
        break
access_token = 'help'
while access_token.lower() == 'help' :
    access_token = input('please inter your access token! if you\'re not sure how to get one enter "help"\n')
    if access_token.lower() == 'help':
        print("to get your client id (used earlier) and access id you can go to https://twitchtokengenerator.com/ go down to the 'available token "
              "scopes and "
              "check the moderator:manage:banned_users scope to enable user banning via an application (specifically this application) and then click on the "
              "'generate token!' botton in green at the end of the list, it'll then take you to the tokens it generated, for this application we'll need the "
              "'access token and the client id, in this case you'll need to copy the access token and paste it here")
    else:
        break
ghead ={'Authorization': 'Bearer ' + access_token, 'Client-Id': client_id}
g = requests.get('https://api.twitch.tv/helix/users?login=' +name, headers=ghead)  # asking twitch for your id based on your name
if g.status_code == 401:
    print('Authorization failed, please check the client id and the access token again')
gjson = json.loads(g.text)
try:
    streamer_id =gjson['data'][0]['id']  # trying to find the user name, if it fails it goes to except, if it succeeds it continues on
except:
    print('didn\'t find user ' + name + ' please try again')  # failed to find the user name error
    exit(2)


print("commence the banning process! (will take some time)")

success_counter = 0
not_exist_counter = 0
already_banned_counter = 0
default = 'ban listed'
line = f.readline().split()
while len(line) > 0:
    ban_name = line[0]
    if len(line) > 2:
        reason = line[1:]
    else:
        reason = default
    ghead ={'Authorization': ('Bearer ' + access_token), 'Client-Id': client_id}
    g = requests.get('https://api.twitch.tv/helix/users?login=' +ban_name, headers=ghead)  # getting the id of the user we want to ban
    while g.status_code == 429:  # made too many requests, there's a limit of 800 requests per minute, so we wait a minute...
        sleep(60)
        g = requests.get('https://api.twitch.tv/helix/users?login=' + ban_name, headers=ghead)  # ...and try again
    gjson = json.loads(g.text)
    try:
        ban_id = gjson['data'][0]['id']  # request was successful but it might be empty (user might not exists)
    except:
        not_exist_counter += 1  # user does not exists, going to the next user
        line = f.readline().split()
        continue

    rheaders = {'Authorization': 'Bearer ' + access_token, 'Client-Id': client_id, 'Content-Type': 'application/json'}  # user exists, so we prepare to ban them
    payload = {'data': {'user_id': ban_id, 'reason': reason}}
    r = requests.post('https://api.twitch.tv/helix/moderation/bans?broadcaster_id='+streamer_id+'&moderator_id='+streamer_id, headers=rheaders, data=json.dumps(
        payload))  # sending a request to ban the user, broadcaster id and moderator id are the same because it should be the broadcaster who bans (or at least with
    # their permission)
    if r.status_code == 200:  # code 200 means success
        success_counter += 1
        line = f.readline().split()
        continue
    elif r.status_code ==429:  # 429 means we did that too many times
        sleep(61)
        r = requests.post('https://api.twitch.tv/helix/moderation/bans?broadcaster_id='+streamer_id+'&moderator_id='+streamer_id, headers=rheaders, data=json.dumps(payload))
    elif r.status_code == 400:  # code 400 means it failed
        err =json.loads(r.text)
        if err['message'] == 'user is already banned':  # if it failed because the user is already banned there's no problem, we just continue forward
            already_banned_counter += 1
            line = f.readline().split()
            continue

        print('something went wrong it\'s all yoyo\'s fault! please tell him "fuck off you cretin" (or you could ask him to help you)')  # if it didn't fail because
        # the user was banned but for some other reason print the error and a very useful message from me
        print(r.text)
        exit(3)
    elif r.status_code == 500:  # pretty self explanatory from the error message
        print('twitch api responded with "internal server error", please try again later')
        exit(4)
    else :
        print('something unexpected has happened, yell at yoyo')  # in case something weird happens, idk shouldn't get here
        exit(5)

print('finished the banning process, banned %d users successfully, %d users were already banned and  %d users did not exists (might have been deleted by twitch). have a '
      'nice day!' % (success_counter, already_banned_counter, not_exist_counter))  # some stats at the end

