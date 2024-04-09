#------------------------------------------------------#
import time
import interactions
from interactions import Button, ButtonStyle, ActionRow
from pymongo import MongoClient
from bson.objectid import ObjectId
from urllib.parse import quote_plus
#------------------------------------------------------#
# Encode your MongoDB username and password
username = quote_plus('username')
password = quote_plus('password')
#------------------------------------------------------#
#Discord Variable for running the bot
#------------------------------------------------------#
bot = interactions.Client(
    token="your token",
    intents=interactions.Intents.DEFAULT | interactions.Intents.GUILD_MESSAGE_CONTENT,)
#------------------------------------------------------#
#MongoDB Variable for connecting to the database
#------------------------------------------------------#
client = MongoClient(f'mongodb+srv://urlConnectionString')

db = client.ZaZaDB
UserCollection = db.users
#------------------------------------------------------#
#Creation of the bot status
#------------------------------------------------------#
@bot.event
async def on_start():
    await bot.change_presence(
        presence=interactions.ClientPresence(
            status=interactions.StatusType.ONLINE,
            activities=[
                interactions.PresenceActivity(
                    name="Helping SMOKINGCORD members",
                    type=interactions.PresenceActivityType.GAME,
                    created_at=int(time.time()),
                    details="sdsds",
                    state="sdsdsd",
                    assets=interactions.PresenceAssets(large_image='logo-real-3d-effect')
                )
            ]
        )
    )
    print("--------------")
    print("Done loading")
    print("--------------")
#------------------------------------------------------#
#Creation of the bot panel command where we will manage all our commands
#------------------------------------------------------#
@bot.command(name='panel',description="Responds with holder verification panel")
async def components_command(ctx: interactions.CommandContext):
    #------------------------------------------------------#
    #Creation of the differents buttons
    #------------------------------------------------------#
    VerificationButton = Button(
        style=ButtonStyle.SUCCESS,
        custom_id="count",
        label="Count your cigarettes"
    )
    OneButton = Button(
        style=ButtonStyle.SUCCESS,
        custom_id="count1",
        emoji=interactions.Emoji(name="1️⃣")

    )
    TwoButton = Button(
        style=ButtonStyle.SUCCESS,
        custom_id="count2",
        emoji=interactions.Emoji(name="2️⃣")
    )

    ThreeButton = Button(
        style=ButtonStyle.SUCCESS,
        custom_id="count3",
        emoji=interactions.Emoji(name="3️⃣")
    )

    DailyButton= Button(
        style=ButtonStyle.PRIMARY,
        custom_id="infodaily",
        label="Check daily stats"
    )

    TotalButton= Button(
        style=ButtonStyle.PRIMARY,
        custom_id="infototal",
        label="Check total stats"
    )
    #------------------------------------------------------#
    #Creation of the main embeed
    #------------------------------------------------------#
    embed = interactions.Embed(title='SMOKINGCORD:', color=0xff0000)
    embed.add_field(name=f"Welcome to the SMOKINGCORD - Bot:", value=f"SMOKINGCORD - Bot helps keeping track of a person's cigarette consumption. By pressing the **1**, **2**, or **3** buttons, the user can add one, two, or three cigarettes to the counter, making the registration process quick and intuitive.\n \nThe bot also allows the user to monitor their cigarette consumption over time and provides statistics such as the daily or weekly average of cigarettes smoked, helping the user make more informed decisions about their health and lifestyle.\n", inline=False)
    embed.set_image(url=f'https://cdn.discordapp.com/attachments/768546282674716677/1078045572990255234/anime-cigarette.gif')
    embed.set_footer(text='SMOKINGCORD - Counter', icon_url='https://cdn.discordapp.com/attachments/768546282674716677/1078045564010237992/anime-boy-smoking.gif')

    action_row1= ActionRow(components=[VerificationButton, OneButton,TwoButton,ThreeButton])
    action_row2= ActionRow(components=[DailyButton,TotalButton])
    await ctx.send(embeds=embed, components=[action_row1,action_row2])

#------------------------------------------------------#
#Creation of the id=count button function
#------------------------------------------------------#
@bot.component("count")
async def count_function(ctx: interactions.ComponentContext):
    text = interactions.TextInput(
        style=interactions.TextStyleType.SHORT,
        label="How much did you smoke?",
        custom_id="text_input_response",
        min_length=1,
        max_length=2,
    )

    modal = interactions.Modal(
        title="Application Form",
        custom_id="mod_app_form",
        components=[text],
    )

    userid= ctx.author.id._snowflake
    datagiorno=ctx.created_at.day
    datamese=ctx.created_at.month
    dataanno=ctx.created_at.year


    query = { "UserId": f"{userid}" }
    # use the count_documents() method to retrieve the number of matching documents
    #num_matching_docs = UserCollection.count_documents(query)

    if (UserCollection.count_documents(query) == 0):
        user = {"UserId": f"{userid}", "Name": f"{ctx.author.name}", "ServerId": f"{ctx.guild.id}","LastUse": f"{datagiorno}/{datamese}/{dataanno}" ,"DailyCount": 0, "TotalCount": 0}
        UserCollection.insert_one(user)
    #------------------------------------------------------#
    #Sending text field pop-up
    #------------------------------------------------------#
    await ctx.popup(modal)
    
@bot.modal("mod_app_form")
async def modal_response(ctx, response: int):

    userid= ctx.author.id._snowflake
    datagiorno=ctx.created_at.day
    datamese=ctx.created_at.month
    dataanno=ctx.created_at.year

    if int(response) >0:

        filter = { "UserId": f"{userid}" }
        # define the update to apply to the document
        date = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "LastUse": 1})

        if  (date['LastUse'] == (f"{datagiorno}/{datamese}/{dataanno}")):


            try:
                print("Adding to the database...")
                # define the filter to find the document to update
                DailyCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "DailyCount": 1})['DailyCount']
                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']
                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatedaily = { "$set": { "DailyCount": DailyCount + int(response) }}
                updatetotal = { "$set": { "TotalCount": TotalCount + int(response) } }
                # update the document
                UserCollection.update_one(filter, updatedaily)
                UserCollection.update_one(filter, updatetotal)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)

        else:

            try:

                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']

                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatelastuse = { "$set": { "LastUse": f"{datagiorno}/{datamese}/{dataanno}"}}
                updatetotal = { "$set": { "TotalCount": TotalCount + int(response) } }
                updatedaily = { "$set": { "DailyCount": int(response) }}
                # update the document
                UserCollection.update_one(filter, updatelastuse)
                UserCollection.update_one(filter, updatetotal)
                UserCollection.update_one(filter, updatedaily)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)
    else:

        await ctx.send(f"Please type a correct value", ephemeral=True)

#------------------------------------------------------#
#Creation of the id=infodaily button function
#------------------------------------------------------#
@bot.component("infodaily")
async def info_function(ctx: interactions.ComponentContext):

    userid= ctx.author.id._snowflake
    datagiorno=ctx.created_at.day
    datamese=ctx.created_at.month
    dataanno=ctx.created_at.year


    query = { "UserId": f"{userid}" }
    # use the count_documents() method to retrieve the number of matching documents
    #num_matching_docs = UserCollection.count_documents(query)

    if (UserCollection.count_documents(query) == 0):
        user = {"UserId": f"{userid}", "Name": f"{ctx.author.name}", "ServerId": f"{ctx.guild.id}","LastUse": f"{datagiorno}/{datamese}/{dataanno}" ,"DailyCount": 0, "TotalCount": 0}
        UserCollection.insert_one(user)

    else:
        date = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "LastUse": 1, "DailyCount": 1})

        if  (date['LastUse'] == (f"{datagiorno}/{datamese}/{dataanno}")):
            await ctx.send(f"You smoked {date['DailyCount']} cigarettes", ephemeral=True)
        else:
            await ctx.send(f"You still need to smoke cigarettes today, congrats", ephemeral=True)

#------------------------------------------------------#
#Creation of the id=infototal button function
#------------------------------------------------------#
@bot.component("infototal")
async def info_function(ctx: interactions.ComponentContext):

    userid= ctx.author.id._snowflake
    datagiorno=ctx.created_at.day
    datamese=ctx.created_at.month
    dataanno=ctx.created_at.year


    query = { "UserId": f"{userid}" }
    # use the count_documents() method to retrieve the number of matching documents
    #num_matching_docs = UserCollection.count_documents(query)

    if (UserCollection.count_documents(query) == 0):
        user = {"UserId": f"{userid}", "Name": f"{ctx.author.name}", "ServerId": f"{ctx.guild.id}","LastUse": f"{datagiorno}/{datamese}/{dataanno}" ,"DailyCount": 0, "TotalCount": 0}
        UserCollection.insert_one(user)

    else:
        date = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "LastUse": 1, "TotalCount": 1})
        await ctx.send(f"You smoked {date['TotalCount']} cigarettes", ephemeral=True)
        

#------------------------------------------------------#
#Creation of the id=count1 button function
#------------------------------------------------------#
@bot.component("count1")
async def add_one_function(ctx: interactions.ComponentContext):
    
    userid= ctx.author.id._snowflake
    datagiorno=ctx.created_at.day
    datamese=ctx.created_at.month
    dataanno=ctx.created_at.year

    query = { "UserId": f"{userid}" }
    # use the count_documents() method to retrieve the number of matching documents
    #num_matching_docs = UserCollection.count_documents(query)

    if (UserCollection.count_documents(query) == 0):
        user = {"UserId": f"{userid}", "Name": f"{ctx.author.name}", "ServerId": f"{ctx.guild.id}","LastUse": f"{datagiorno}/{datamese}/{dataanno}" ,"DailyCount": 0, "TotalCount": 0}
        UserCollection.insert_one(user)

    else:

        date = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "LastUse": 1})

        if  (date['LastUse'] == (f"{datagiorno}/{datamese}/{dataanno}")):


            try:
                print("Adding to the database...")
                # define the filter to find the document to update
                DailyCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "DailyCount": 1})['DailyCount']
                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']
                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatedaily = { "$set": { "DailyCount": DailyCount + 1 }}
                updatetotal = { "$set": { "TotalCount": TotalCount + 1 } }
                # update the document
                UserCollection.update_one(filter, updatedaily)
                UserCollection.update_one(filter, updatetotal)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)

        else:

            try:

                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']

                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatelastuse = { "$set": { "LastUse": f"{datagiorno}/{datamese}/{dataanno}"}}
                updatetotal = { "$set": { "TotalCount": TotalCount + 1 } }
                updatedaily = { "$set": { "DailyCount": 1 }}
                # update the document
                UserCollection.update_one(filter, updatelastuse)
                UserCollection.update_one(filter, updatetotal)
                UserCollection.update_one(filter, updatedaily)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)

#------------------------------------------------------#
#Creation of the id=count2 button function
#------------------------------------------------------#
@bot.component("count2")
async def add_one_function(ctx: interactions.ComponentContext):
    
    userid= ctx.author.id._snowflake
    datagiorno=ctx.created_at.day
    datamese=ctx.created_at.month
    dataanno=ctx.created_at.year

    query = { "UserId": f"{userid}" }
    # use the count_documents() method to retrieve the number of matching documents
    #num_matching_docs = UserCollection.count_documents(query)

    if (UserCollection.count_documents(query) == 0):
        user = {"UserId": f"{userid}", "Name": f"{ctx.author.name}", "ServerId": f"{ctx.guild.id}","LastUse": f"{datagiorno}/{datamese}/{dataanno}" ,"DailyCount": 0, "TotalCount": 0}
        UserCollection.insert_one(user)

    else:

        date = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "LastUse": 1})

        if  (date['LastUse'] == (f"{datagiorno}/{datamese}/{dataanno}")):


            try:
                print("Adding to the database...")
                # define the filter to find the document to update
                DailyCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "DailyCount": 1})['DailyCount']
                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']
                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatedaily = { "$set": { "DailyCount": DailyCount + 2 }}
                updatetotal = { "$set": { "TotalCount": TotalCount + 2 } }
                # update the document
                UserCollection.update_one(filter, updatedaily)
                UserCollection.update_one(filter, updatetotal)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)

        else:

            try:

                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']

                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatelastuse = { "$set": { "LastUse": f"{datagiorno}/{datamese}/{dataanno}"}}
                updatetotal = { "$set": { "TotalCount": TotalCount + 2 } }
                updatedaily = { "$set": { "DailyCount": 2 }}
                # update the document
                UserCollection.update_one(filter, updatelastuse)
                UserCollection.update_one(filter, updatetotal)
                UserCollection.update_one(filter, updatedaily)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)

#------------------------------------------------------#
#Creation of the id=count3 button function
#------------------------------------------------------#
@bot.component("count3")
async def add_one_function(ctx: interactions.ComponentContext):
    
    userid= ctx.author.id._snowflake
    datagiorno=ctx.created_at.day
    datamese=ctx.created_at.month
    dataanno=ctx.created_at.year

    query = { "UserId": f"{userid}" }
    # use the count_documents() method to retrieve the number of matching documents
    #num_matching_docs = UserCollection.count_documents(query)

    if (UserCollection.count_documents(query) == 0):
        user = {"UserId": f"{userid}", "Name": f"{ctx.author.name}", "ServerId": f"{ctx.guild.id}","LastUse": f"{datagiorno}/{datamese}/{dataanno}" ,"DailyCount": 0, "TotalCount": 0}
        UserCollection.insert_one(user)

    else:

        date = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "LastUse": 1})

        if  (date['LastUse'] == (f"{datagiorno}/{datamese}/{dataanno}")):


            try:
                print("Adding to the database...")
                # define the filter to find the document to update
                DailyCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "DailyCount": 1})['DailyCount']
                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']
                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatedaily = { "$set": { "DailyCount": DailyCount + 3 }}
                updatetotal = { "$set": { "TotalCount": TotalCount + 3 } }
                # update the document
                UserCollection.update_one(filter, updatedaily)
                UserCollection.update_one(filter, updatetotal)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)

        else:

            try:

                TotalCount = UserCollection.find_one({"UserId": f"{userid}"}, {"_id": 0, "TotalCount": 1})['TotalCount']

                filter = { "UserId": f"{userid}" }
                # define the update to apply to the document
                updatelastuse = { "$set": { "LastUse": f"{datagiorno}/{datamese}/{dataanno}"}}
                updatetotal = { "$set": { "TotalCount": TotalCount + 3 } }
                updatedaily = { "$set": { "DailyCount": 3 }}
                # update the document
                UserCollection.update_one(filter, updatelastuse)
                UserCollection.update_one(filter, updatetotal)
                UserCollection.update_one(filter, updatedaily)

                await ctx.send(f"Data updated thanks", ephemeral=True)

            except:

                await ctx.send(f"Please type a correct value", ephemeral=True)

#------------------------------------------------------#
#------------------------------------------------------#
bot.start()
#------------------------------------------------------#
