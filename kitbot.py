import os

import discord
from dotenv import load_dotenv
import io
import re
import datetime

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
validToons = os.getenv('VALID_TOONS').split(',')

client = discord.Client()

snapshots = []

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    

@client.event
async def on_message(message):

    if message.content == "!stop": await client.logout()
    
    if not type(message.channel) == discord.DMChannel:
        return
    if message.author == client.user:
        return
    if not message.attachments:
        return
        
    for att in message.attachments:
        print(att.filename)
        if not att.filename[:-4] in validToons:
            return
        record = {
            "charName": att.filename[:-4],
            "recordDate": datetime.datetime.now(),
            "isMostRecent": True,
            "hash": '',
            "items":[],
        }
        if snapshots:
            for item in snapshots:
                if item['charName'] == record['charName']:
                    item['isMostRecent'] = False
        
        contents = await att.read()
        open(att.filename, 'wb').write(contents)
        with open(att.filename) as f:
            record['hash'] = hash(f.read())
            
            hashCheck = list(filter(lambda x: x["hash"]== record["hash"], snapshots))
            
            if len(hashCheck) == 1:            
                hashCheck = hashCheck[0]
                print("warning possible duplicate date from " + str(hashCheck['recordDate']))
                return 
                
                
            line = f.readline().strip('\n')
            while line:
                if re.match("Bank.-", line) or re.match("General.-", line):
                    line = line.split('\t')
                    location = re.findall("\d",line[0])
                    record['items'].append({
                        "name": line[1],
                        "id": line[2],
                        "bag": location[0],
                        "loc": location[1],
                        "count": line[3],
                    })
                    
                
                
                line = f.readline().strip('\n')
        snapshots.append(record)
        for item in snapshots:
            print(item["recordDate"])
            print(item["hash"])
        
        
client.run(token)