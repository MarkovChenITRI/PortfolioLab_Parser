from linebot import LineBotApi
from linebot.models import TextSendMessage

def LineBotMessage(text='Meow!!!'):
  line_bot_api = LineBotApi('Es+feMvp7Uwg+nIcgB66iAKWVD1dOKRcXzYwPmSbko+b0Vf21iko3s7dRwEFX1tfToR8mrW78XUACEd/uyecCF/Uqd9LgvkchpPEPiODdX4L8BU4b6pXHzFvlDoAfsP9xIFSMG+rmVzQURS+7uBnegdB04t89/1O/w1cDnyilFU=')
  line_bot_api.push_message('Udba3ff0abbe6607af5a5cfc2e2ddc8a1', TextSendMessage(text=text))
