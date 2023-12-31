import discord
from discord import app_commands
from discord.ext import commands
import os
from keep_alive import keep_alive
import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from data import user_data_fuckyou
from db import save

bot = commands.Bot(command_prefix="^_-", intents=discord.Intents.all())

email = os.environ['email']
password = os.environ['password']

CARRIERS = {
    "att": "@mms.att.net",
    "tmobile": "@tmomail.net",
    "verizon": "@vtext.com",
    "sprint": "@messaging.sprintpcs.com"
}

user_data = [
    
]

def remove_items(test_list, item):
 
    # using list comprehension to perform the task
    res = [i for i in test_list if i != item]
 
    return res

@bot.event
async def on_ready():
    print("Logged in.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

@bot.event
async def on_voice_state_update(member, before, after):
    # Check if the member is the target user
    global user_data
    if member.id in user_data:
        if after.channel:  # Member joined a voice channel
            await member.move_to(None)
    if(member.id in user_data_fuckyou["mutes"]):
        if(user_data_fuckyou["mutes"][member.id]['time'] != 0):
            await member.move_to(None)
@bot.event
async def on_message(message):
    if(message.author.id in user_data_fuckyou["mutes"]):
        if(user_data_fuckyou["mutes"][message.author.id]['time'] != 0):
            await message.delete()
	

@bot.tree.command(name="addtovcblock")
@app_commands.describe(user="User.")
async def addtovcblock(interaction: discord.Interaction, user: discord.User):
    global user_data
    if interaction.user.guild_permissions.administrator:
        user_data.append(user.id)
        await interaction.response.send_message(f"Added {user.display_name} to the vc block.", ephemeral=True)
        await user.move_to(None)
    else:
        await interaction.response.send_message(
            f"You don't have the perms to do this.", ephemeral=True)
        


@bot.tree.command(name="fuckyou")
@app_commands.describe(user="User.")
async def fuckyou(interaction: discord.Interaction, user: discord.User):
    global user_data
    global user_data_fuckyou

    '''
    user_data_fuckyou tree:

    {
        "mutes": {
            "USERID1": {
                "name": "Bob",
                "id": USERID1,
                "time": 50
            }
        },
        "cooldowns": {
            "USERID2": {
                "name": "Bob",
                "time": 110,
                "id": USERID2
            }
        }
    }

    
    '''

    continueVar = False

    if interaction.user.id in user_data_fuckyou["cooldowns"]:
        user_info = user_data_fuckyou["cooldowns"][interaction.user.id]
        print(user_info)
        if(user_info["time"] == 0):
            continueVar = True
        else:
            await interaction.response.send_message(f"You are still on cooldown for {user_info['time']} seconds.")
    else:
        continueVar = True
        user_data_fuckyou["cooldowns"][interaction.user.id] = {
            "time": 0,
            "name": interaction.user.name,
            "id": interaction.user.id
        }


    if(continueVar == True):
        if user.id in user_data_fuckyou["mutes"]:
            user_info = user_data_fuckyou["mutes"][user.id]
            if(user_info["time"] != 0):
                await interaction.response.send_message(f"User is already fuckyou'd. Wait {user_info['time']} seconds.")
                continueVar = False
            else:
                await interaction.response.send_message(f"You have fuckyou'd {user.name}.")
                user_data_fuckyou["cooldowns"][interaction.user.id]["time"] = 60
                user_data_fuckyou["mutes"][user.id]["time"] = 60
                await user.move_to(None)
                await user.send(f"You have been fuckyou'd by {interaction.user.name}")
        else:
            await interaction.response.send_message(f"You have fuckyou'd {user.name}.")
            user_data_fuckyou["cooldowns"][interaction.user.id]["time"] = 60
            await user.move_to(None)
            user_data_fuckyou["mutes"][user.id] = {
                "name": user.name,
                "id": user.id,
                "time": 0
            }
            user_data_fuckyou["mutes"][user.id]["time"] = 60
            await user.send(f"You have been fuckyou'd by {interaction.user.name}")
            

    if(continueVar == True):
        save(user_data_fuckyou)
        
        while(user_data_fuckyou["mutes"][user.id]["time"] != 0):
            user_data_fuckyou["mutes"][user.id]["time"] -= 1
            print(user_data_fuckyou)
            await asyncio.sleep(1)

        while(user_data_fuckyou["cooldowns"][interaction.user.id]["time"] != 0):
            user_data_fuckyou["cooldowns"][interaction.user.id]["time"] -= 1
            print(user_data_fuckyou)
            await asyncio.sleep(1)


    save(user_data_fuckyou)
    

@bot.tree.command(name="sendmessage", description="Send an email/text message to someone.")
@app_commands.describe(type="Type of message you want to send. Email or phone (keep lowercase).", toadress="Adress/phone number.", provider="Provider of the phone number, if you want to just email, feel free to leave this as just a space or a random set of text.", towhoname="To who you want to send it to, (name). Leave empty if you are sending sms.", fromwhoname="From who you want them to see it was, the email will be the same but this will be the display name. Leave empty if you are sending sms.", subject="Subject of the email. Only use if email.", message="The message you want to send.")
async def sendmessage(interaction: discord.Interaction, type: str, toadress: str, provider: str, towhoname: str, fromwhoname: str, subject: str, message: str):
    if(type == "email"):
        message1 = MIMEMultipart()
        fromaddr = ""
        toaddrs = toadress
        message1["To"] = towhoname
        message1["From"] = fromaddr
        message1["Subject"] = subject
        messageText = MIMEText(message,'html')
        message1.attach(messageText)
        server.sendmail(fromaddr,toaddrs,message1.as_string())
        await interaction.response.send_message("Sent", ephemeral=True)
    elif(type == "phone"):
        message1 = MIMEMultipart()
        fromaddr = ""
        toaddrs = toadress + CARRIERS[provider]
        message1["To"] = ""
        message1["From"] = fromaddr
        message1["Subject"] = ""
        messageText = MIMEText(message,'html')
        message1.attach(messageText)
        server.sendmail(fromaddr,toaddrs,message1.as_string())
        await interaction.response.send_message("Sent", ephemeral=True)
    else:
        await interaction.response.send_message("Wrong input, its email or phone, nothing else.", ephemeral=True)




@bot.tree.command(name="removefromvcblock")
@app_commands.describe(user="User.")
async def removefromvcblock(interaction: discord.Interaction, user: discord.User):
    global user_data
    if interaction.user.guild_permissions.administrator:
        user_data = remove_items(user_data, user.id)
        await interaction.response.send_message(f"Removed {user.display_name} from the vc block.", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"You don't have the perms to do this.", ephemeral=True)

@bot.tree.command(name="addeveryonetovcblock")
@app_commands.describe()
async def addeveryonetovcblock(interaction: discord.Interaction):
    global user_data
    if interaction.user.guild_permissions.administrator:
        guild = interaction.guild
        users = [member for member in guild.members]
        for user in users:
            await user.move_to(None)
            user_data.append(user.id)
        await interaction.response.send_message(f"Added everyone to the vc block.", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"You don't have the perms to do this.", ephemeral=True)

@bot.tree.command(name="clearvcblock")
@app_commands.describe()
async def clearvcblock(interaction: discord.Interaction):
    global user_data
    if interaction.user.guild_permissions.administrator:
        user_data = []
        await interaction.response.send_message(f"Cleared the vc block.", ephemeral=True)
    else:
        await interaction.response.send_message(
            f"You don't have the perms to do this.", ephemeral=True)


server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo('Gmail')
server.starttls()
server.login(email,password)

keep_alive()
bot.run(os.environ['TOKEN'])
