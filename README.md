# KitsuMakerBot (Syntaxer)

This bot creates chatbots for **Telegram**.

## Setting Up
Change values in Files/jsons/config.json:
- Set owner_id with your Telegram ID
- Set maker_token with your botmaker token
- Set lastfm_token with a lastfm token (optional)

## Running
Run MainKitsu.py

## Tips
Please /start your bot at least one time before starting Syntaxer.

Your main bot actually works as a clone bot too.  
If you want an user to have more than one bot add his username in Foos.limits and how many bots he can have.  
By default it is set to use threaded requests, but, if you have more than 30 bots i suggest you to use the webhook mode (sperimental).  
There's a really nice guide on how to use Kitsubots: [here](http://telegra.ph/Come-creare-un-KitsuBot-08-20)  
...more to come.


## Dependencies
* requests
* psutil
* schedule

python3 -m pip install requests psutil schedule

This is one of my first projects, the code is not really consistent and there are lots of bugs...
But it works and someone may need it, so here it is!
