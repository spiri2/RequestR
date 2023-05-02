# About Requestr
Requestr allows server owners to keep their "request" channels organized. Whether you get 10, 100, or 1,000 requests by your community, request bot keeps requests inside an embed.  

## Configuration

Clone the repo: `git clone https://github.com/spiri2/RequestR.git`

Set your desired prefix and add your bot token in `bot.py`

Add your Guild ID in `cogs/request.py` - `line 198` and `cogs/staff.py` `line 82`

## Permissions needed: 

• Read Messages

• Send Messages

• Manage Messages (only needed for a specific channel)

## Admin Setup:
There are two commands you need to use to setup Request bot.  

`/setdump` command is for the channel that will post the users requests inside an embed.

`/setrequests` command is to register the public request channel. 

## Admin Commands:
`/unrequest #` command allows the admin to remove a specific request from the embed list

`/edit # <message>` command allows the admin to overwrite a specific request that currently exists.

## User Command
`/request` is the slash command that your community will use to make requests 

## Anti-Spam
The bot will automatically delete any message that doesn't follow after using `/request` command. This is to ensure the channel remains free from unnecessary messages and only show requests. Users with `manage messages` perms are exempt from this 

Add the request channel ID on line 23 `self.restricted_channel = CHANNEL ID HERE`
