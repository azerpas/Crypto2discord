#coding=utf-8
import requests, json, datetime, time, re, BeautifulSoup

s = requests.session()

channelID = 0 # INPUT YOUR DEFAULT CHANNEL ID

#channels = [] # [{''}]

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
	'mobile':{'activated':False,'specific_channel':True,'channel_id':""},

	'ico':{'channel_id':''} # INPUT YOUR 'SPECIFIC' CHANNEL ID FOR ICO ALERT

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
		self.url_ico = "https://discordapp.com/api/channels/{}/messages".format(params['ico']['channel_id'])


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

class ico():
	def __init__(self):
		self.hpages = 3
		self.url = "https://icobench.com/icos?filterSort=rating-desc&page="
		self.s = requests.session()
		self.book = []
		self.r = None

	def scrape(self):
		log("Scraping ICO data...")
		for i in range(1,self.hpages+1):
			req = self.s.get(self.url+str(i))
			soup = BeautifulSoup.BeautifulSoup(req.text)

			for i in soup.findAll("div",{"class":"rate color5"}):
				current_ico = (i.parent.parent)
				if not "ico_data" in str(current_ico):
					continue
				for z in current_ico.findAll("div"):
					if "Start" in z.text and "End" in z.text:
						pass
					if "Start" in z.text:
						pattern = re.compile("Start:(.*)")
						start_date = re.findall(pattern,z.text)
					if "End" in z.text:
						pattern = re.compile("End:(.*)")
						end_date = re.findall(pattern,z.text)
				for z in current_ico.findAll("a"):
					if "href" in str(z):
						pattern = re.compile('href="(.*)">')
						link = re.findall(pattern,str(z))
				title = current_ico.find("a",{"class":"name"})
				pattern = re.compile("""href="/ico/(.*)">""")
				title = re.findall(pattern,str(title))
				title = title[0].replace('-',' ').title()

				for z in current_ico.findAll("div",{"class":"content"}):
					for p in z.findAll("p"):
						description = p.text
				try:
					sep = "KYC"
					description = description.split(sep,1)[0]
				except Exception as e:
					pass

				rating = float(i.text)

				start_date = start_date[0]
				end_date = end_date[0]
				link = "https://icobench.com" + link[0]
				self.book.append({'title':title,'start':start_date,'end':end_date,'description':description,'link':link,'rating':rating})

		maxi = self.book[0]['rating']
		self.r = {'weekWinner':self.book[0]['title'],'rate':maxi}
		for i in range(0,len(self.book)):
			if self.book[i]['rating'] > maxi:
				maxi = self.book[i]['rating']
				self.r['rate'] = maxi
				self.r['weekWinner'] = self.book[i]['title']
		log("Scraped successfully")


	def syntax(self):
		message = "📈 Meilleure ICO de ces 4 derniers jours: " + self.r['weekWinner'] + " avec un score de: " + str(self.r['rate']) + "/5\n\n"
		cutting = 0
		for i in range(0,len(self.book)):
			cutting += 1
			message += "\nNom: {}\nDescription: {}\nDébut: {}\nFin: {}\nLien: {}\nNote: {}\n----------------\n".format(self.book[i]['title'],self.book[i]['description'],self.book[i]['start'],self.book[i]['end'],self.book[i]['link'],self.book[i]['rating'])
			if (cutting % 3) == 0:
				message += "+++"
		# adapted to ICObench syntax
		return message




if __name__ == "__main__":
	CMC = CMC()
	D = Discord()
	I = ico()
	count = 0
	while True:
		r = CMC.scrape(params)
		r = D.encode(r)
		TOPmessage = D.top(r)
		MOBmessage = D.mobile_notif(r)
		D.send(TOPmessage,D.url)
		if count == 0:
			I.scrape()
			ICOmessage = I.syntax()
			ICOmessage = ICOmessage.split("+++")
			D.send("📍ICO recap📍",D.url_ico)
			for i in ICOmessage:
				D.send(i,D.url_ico)
		if count == 288: # 345600 (4 days) / 1200 = 288 / Each 4 days -> alert
			I.book = []
			ICOmessage = I.syntax()
			ICOmessage = ICOmessage.split("+++")
			D.send("📍ICO recap📍",D.url_ico)
			for i in ICOmessage:
				D.send(i,D.url_ico)
			count = 1
		count += 1
		I.book = [] # need to be changed
		if params['mobile']['activated'] == True:
			print("")
			D.send(MOBmessage,D.url_mobile)
		time.sleep(1200)
