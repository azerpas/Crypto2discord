#coding=utf-8
import requests, json, datetime, time

s = requests.session()

channelID = 0 # INPUT YOUR DEFAULT CHANNEL ID

channels = [] # [{''}]

botToken = '' # INPUT YOUR BOT TOKEN


# DEFAULT PARAMS - CHANGE THEM IF NEEDED 
params = {
	'method':0, # 0 for list, 1 for specific currency,

	# Method 0 (List)
	'limit':20, # number of currencies to scrape
	# Starting at a specific position? 
	'specific_pos':False,
	'position':1, # Indicate specific position

	# Method 1 (Specific currency)
	'name':'bitcoin', # input name of currency (check currency url to get his id) Ex: bitcoin, iota, ripple, etc...

	# Mobile syntax alert activated ?
	'mobile':{'activated':True,'specific_channel':True,'channel_id':"000000000"}
}

def log(event):
	print(datetime.datetime.now().strftime('%H:%M') + " :: @azerpas@ :: " + str(event))

class CMC():
	def __init__(self):
		self.s = requests.session()
		self.currency = "https://api.coinmarketcap.com/v1/ticker/" # + the currency we want (specific currency)
		self.start_position = 1 # which start position 
		self.limit = 1 # how much currency from start position
		self.top = "?limit={}".format(params['limit']) # + how much currencies
		self.start = "?start={}&limit={}".format(params['position'],params['limit'])
		self.convert = {'active':False,'fiat':'EUR'} # "AUD", "BRL", "CAD", "CHF", "CLP", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "IDR", "ILS", "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD", "PHP", "PKR", "PLN", "RUB", "SEK", "SGD", "THB", "TRY", "TWD", "ZAR"

	def scrape(self,params):
		log('Scraping with method: ' + str(params['method']))
		if params['method'] == 0:
			if params['specific_pos'] == True:
				log('Specific position option actived')
				rurl = self.currency + self.start
				r = self.s.get(rurl)
				log('Scraped successfully') if(r.status_code == 200) else log("Can't scrape")
				return r.text
			else:
				rurl = self.currency + self.top
				r = self.s.get(rurl)
				log('Scraped successfully') if(r.status_code == 200) else log("Can't scrape")
				return r.text
		else:
			rurl = self.currency + params['name']
			r = self.s.get(rurl)
			log('Scraped successfully') if(r.status_code == 200) else log("Can't scrape")
			return r.text


class Discord():
	def __init__(self):
		self.token = botToken
		self.s = requests.session()
		self.headers = { "Authorization":"Bot {}".format(self.token),"User-Agent":"azerpas (http://azerpas.io, v1.0)","Content-Type":"application/json", }
		self.default_channel = channelID
		self.url = "https://discordapp.com/api/channels/{}/messages".format(self.default_channel)
		self.url_mobile = "https://discordapp.com/api/channels/{}/messages".format(params['mobile']['channel_id'])


	def send(self,content,channel):
		log('Sending infos to Discord channel(s)')
		# Need to add multiple channel sending
		message =  json.dumps ( {"content":content} )
		r = requests.post(channel, headers = self.headers, data = message)
		log('Infos sent successfully') if(r.status_code == 200) else log("Can't send infos")
		# Need to add an alert in case if it can't send the infos anymore, like contact channel owner...

	def encode(self,content):
		ret = content.encode('ascii','ignore')
		ret = json.loads(ret)
		return ret



	def top(self,content):
		message = """
-------------------------⏰ """ + datetime.datetime.now().strftime("%H:%M:%S") + """⏰ -------------------------"""
		message += """
--------------------------------------------------------------------
Rank | Name | Price | Change(1h) | Change(24h) | Change(7d)
--------------------------------------------------------------------
		"""
		for i in content:
			message += """
{}    |    {}    |    {}    |    {}    |    {}    |    {}
			""".format(i['rank'],i['symbol'],i['price_usd'][:6]+" $",i['percent_change_1h']+" %",i['percent_change_24h']+" %",i['percent_change_7d']+" %")
		message += """
		"""
		return message

	def mobile_notif(self,content):
		message = """⏰: {} | """.format(datetime.datetime.now().strftime("%H:%M"))
		for i in content:
			message += """{} : {}$ | """.format(i['symbol'],i['price_usd'][:6])
		message += """
		"""
		return message




if __name__ == "__main__":
	CMC = CMC()
	D = Discord()
	while True:
		r = CMC.scrape(params)
		r = D.encode(r)
		message = D.top(r)
		message2 = D.mobile_notif(r)
		D.send(message,D.url)
		if params['mobile']['activated'] == True:
			D.send(message2,D.url_mobile)
		time.sleep(600)

