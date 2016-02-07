#example listen

from . import bot

@bot.listen('Hello')
def helloworld(message):
	bot.reply(' world!')
	print('Reply successfully sent! Hello world!')
	
@bot.catchall
def testit(message):
	bot.reply(' world!')
	print('ayy lmao')
