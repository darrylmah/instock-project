from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import urllib.parse
import tweepy
import functions
import time
import asyncio
import secrets

username = urllib.parse.quote_plus(secrets.username)
password = urllib.parse.quote_plus(secrets.password)

client = MongoClient(secrets.mongo_url, secrets.mongo_port)

consumer_key = secrets.consumer_key
consumer_secret = secrets.consumer_secret
access_token = secrets.access_token
access_token_secret = secrets.access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,
    wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

# screen_name = "bananashark2"

# user = api.get_user(screen_name)
# recipient_id = user.id_str

# print(recipient_id)

display = Display(visible=0, size=(800, 600))
display.start()
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(executable_path=secrets.user_path, options=options)

# driver = webdriver.Firefox()

db = client.twitter
messages = db.messages
camille_id = secrets.camille_id
self_id = secrets.self_id

#outer loop
while(True) :

    #driver = webdriver.Firefox()
    driver = webdriver.Chrome(executable_path=secrets.user_path, options=options)

    start_time = time.time()

    try :
        direct_messages = api.list_direct_messages(100)
        print("obtained direct messages")
    except :
        api.verify_credentials()
        print("Authentication OK")
        direct_messages = api.list_direct_messages(100)
        print("obtained direct messages")
    finally : 
        print("error collection direct messages")
        break

    received_messages = []
    valid_messages = []
    sent_messages = []

    links_array = []

    #build valid incoming messages array to add new links to DB
    for message in direct_messages :
        if self_id in message.message_create["sender_id"] :
            sent_messages.append(message)
            print("building sent messages array")
        elif camille_id in message.message_create["sender_id"] :
            valid_messages.append(message)
            print("building valid messages array")
        else :
            received_messages.append(message)
            print("building other received messages array")

    #clear out old sent messages
    for message in sent_messages :
        api.destroy_direct_message(message.id)
        print("deleted message " + message.id)

    #clear out recieved messages from non-valid user
    for message in received_messages :
        recipient_id = message.message_create["sender_id"]
        api.destroy_direct_message(message.id)
        print("non valid message deleted " + message.id)

    #work with valid messages from user
    for message in valid_messages :
        recipient_id = message.message_create["sender_id"]
        #verify url
        if functions.contains_url(message) == True :
            #check if url already in DB
            if functions.url_already_exists(message, messages) == False :
                message_data = {
                "message_id" :  message.id,
                "recipient_id" : message.message_create["target"]["recipient_id"],
                "sender_id" : message.message_create["sender_id"],
                "message_text" : message.message_create["message_data"]["text"],
                "link": message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"]
                }
                messages.insert_one(message_data)
                print("data has been added")
                api.send_direct_message(recipient_id, "Your link has been added",
                attachment_media_id=message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"])
                api.destroy_direct_message(message.id)
                print("message was sent to user. ADD")
            #check if user requests to delete url    
            elif "delete" in message.message_create["message_data"]["text"].lower() :
                print(message.message_create["message_data"]["text"].lower())
                try :
                    messages.find_one_and_delete({"link" : message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"]})
                    print(message.message_create["message_data"]["entities"]["urls"][0]["expanded_url"] + " deleted from db")
                    api.send_direct_message(recipient_id, "We removed your link")
                    api.destroy_direct_message(message.id)
                    print("message sent to user. DELETE")
                except :
                    print("link not in database")
                    api.destroy_direct_message(message.id)
            else :
                print("url already exists in database")
                api.send_direct_message(recipient_id, "url already exists in database. Respond with 'delete' and url, if you wish to delete url from database.")
            
        #wip adding ability for user to check current urls in DB. running into issue of not being able to send all links
        #elif "search" in message.message_create["message_data"]["text"].lower() :
            #functions.return_search(recipient_id, message, messages, api)
        #respond to valid user if no link is in message, with instructions
        else :
            api.send_direct_message(recipient_id,
                "Please include url to track, or type 'delete' and include url you wish to remove from tracker, or type 'seach' to show list of links")
            api.destroy_direct_message(message.id)
            print("no url in message")

    #build links array from DB
    for item in messages.find() :
        links_array.append(item["link"])

    #inner loop running to check websites
    while(True) :

        current_time = time.time()
        elapsed_time = current_time - start_time

        if elapsed_time > 300 :
            print("loop running for over 5 minutes. Restarting")
            driver.quit()
            break        

        for link in links_array :
            isPresent = []
            if "https://www.amazon.com" in link :
                asyncio.run(functions.amazon_main(driver, link, WebDriverWait, EC, By, api, links_array))
            elif "https://seaworldparksshop.com" in link :
                asyncio.run(functions.seaworld_main(driver, link, WebDriverWait, EC, By, api, links_array))
            elif "https://www.walgreens.com" in link :
                asyncio.run(functions.walgreens_main(driver, link, WebDriverWait, EC, By, api, links_array))
            elif "https://www.walmart.com" in link :
                asyncio.run(functions.walmart_main(driver, link, WebDriverWait, EC, By, api, links_array))
            elif "https://cedarpointonlineshop.com" in link :
                asyncio.run(functions.cedar_main(driver, link, WebDriverWait, EC, By, api, links_array))            


# api.send_direct_message(recipient_id,new_status, attachment_media_id=url_link)
