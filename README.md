# INUKO Finance reflection bot for telegram
Telegram groups / private chats need to register at the bot to get automatic information about new reflections payout.<br>
Its not required to get the chat registered if you only want to get the last saved balance on demand.<br>

To use the bot, add the bot **@inukoreflectionbot** in Telegram group or create a new private chat with this bot.
You can register with command  **/register_inukoreflection_bot**<br>
To unregister type follwing command **/unregister_inukoreflection_bot**<br>
It is always possible to get the last saved balance by executing the following command: **/balance_inukoreflection_bot**<br>
You can get help with command **/help**<br><br>

After registration only the chatid of the telegram group / private chat will be written to a SQLite database<br>
With unregistration this entry will be deleted. <br><br>

required API-KEYs are now stored in file inuko_config.py. There is an exampe file called inuko_config.py.example in repository. Just copy it to inuko_config.py and change the API keys as you require.

