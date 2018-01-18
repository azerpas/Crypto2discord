#coding=utf-8
import requests, json, datetime, time

s = requests.session()

channelID = # Insert your channel ID here

# channels = [] # [{''}]

botToken = '' # Insert your bot token here


# DEFAULT PARAMS - CHANGE THEM IF NEEDED 
params = {
	'method':0, # 0 for list, 1 for specific currency

	# Method 0 (List)
	'limit':20, # number of currencies to scrape
	# Starting at a specific position? 
	'specific_pos':False,
	'position':1, # Indicate specific position

	# Method 1 (Specific currency)
	'name':'bitcoin', # input name of currency (check currency url to get his id) Ex: bitcoin, iota, ripple, etc...
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


	def send(self,content):
		log('Sending infos to Discord channel(s)')
		# Need to add multiple channel sending
		message =  json.dumps ( {"content":content} )
		r = requests.post(self.url, headers = self.headers, data = message)
		log('Infos sent successfully') if(r.status_code == 200) else log("Can't send infos")
		# Need to add an alert in case if it can't send the infos anymore, like contact channel owner...

if __name__ == "__main__":
	CMC = CMC()
	D = Discord()
	while True:
		message = """
--------------------------------------------------------------------
Rank | Name | Price | Change(1h) | Change(24h) | Change(7d)
--------------------------------------------------------------------
		"""
		r = CMC.scrape(params)
		#D.send("TESTING")
		r = r.encode('ascii','ignore')
		rjson = json.loads(r)
		for i in rjson:
			message += """
{}    |    {}    |    {}    |    {}    |    {}    |    {}
			""".format(i['rank'],i['symbol'],i['price_usd'][:6]+" $",i['percent_change_1h']+" %",i['percent_change_24h']+" %",i['percent_change_7d']+" %")
		print(message)
		D.send(message)
		time.sleep(600)

