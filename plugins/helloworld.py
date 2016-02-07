#example listen

from . import bot

@bot.listen('Hello')
def helloworld(message, comment):
	bot.reply(' world!')
	print('Reply successfully sent! Hello world!')
	
@bot.catchall
def testit(message, comment):
	bot.reply(' world!')
	print('ayy lmao')
