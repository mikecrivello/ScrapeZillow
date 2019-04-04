from lxml import html
import requests
import unicodecsv as csv
import argparse

def parse(zipcode, filter = None):

	if filter == "newest":
		url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/days_sort".format(zipcode)
	elif filter == "cheapest":
		url = "https://www.zillow.com/homes/for_sale/{0}/0_singlestory/pricea_sort/".format(zipcode)
	else:
		url = "https://www.zillow.com/homes/for_sale/{0}_rb/?fromHomePage=true&shouldFireSellPageImplicitClaimGA=false&fromHomePageTab=buy".format(zipcode)

	for i in range(5):
		headers= {
					'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
					'accept-encoding':'gzip, deflate, sdch, br',
					'accept-language':'en-GB,en;q=0.8,en-US;q=0.6,ml;q=0.4',
					'cache-control':'max-age=0',
					'upgrade-insecure-requests':'1',
					'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
				 }
		response = requests.get(url,headers = headers)
		print(response.status_code)
		parser = html.fromstring(response.text)
		searchResults = parser.xpath("//div[@id='search-results']//article")
		propertiesList = []

		for properties in search_results:
			rawAddress = properties.xpath(".//span[@itemprop='address']//span[@itemprop='streetAddress']//text()")
			rawCity = properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressLocality']//text()")
			rawState= properties.xpath(".//span[@itemprop='address']//span[@itemprop='addressRegion']//text()")
			rawPostalCode= properties.xpath(".//span[@itemprop='address']//span[@itemprop='postalCode']//text()")
			rawPrice = properties.xpath(".//span[@class='zsg-photo-card-price']//text()")
			rawInfo = properties.xpath(".//span[@class='zsg-photo-card-info']//text()")
			rawBrokerName = properties.xpath(".//span[@class='zsg-photo-card-broker-name']//text()")
			url = properties.xpath(".//a[contains(@class,'overlay-link')]/@href")
			rawTitle = properties.xpath(".//h4//text()")

			address = ' '.join(' '.join(rawAddress).split()) if rawAddress else None
			city = ''.join(rawCity).strip() if rawCity else None
			state = ''.join(rawState).strip() if rawState else None
			postalCode = ''.join(rawPostalCode).strip() if rawPostalCode else None
			price = ''.join(rawPrice).strip() if rawPrice else None
			info = ' '.join(' '.join(rawInfo).split()).replace(u"\xb7",',')
			broker = ''.join(rawBrokerName).strip() if rawBrokerName else None
			title = ''.join(rawTitle) if rawTitle else None
			propertyUrl = "https://www.zillow.com"+url[0] if url else None
			isForsale = properties.xpath('.//span[@class="zsg-icon-for-sale"]')
			properties = {
							'address':address,
							'city':city,
							'state':state,
							'postal_code':postalCode,
							'price':price,
							'facts and features':info,
							'real estate provider':broker,
							'url':propertyUrl,
							'title':title
			}
			if isForsale:
				propertiesList.append(properties)
		return propertiesList


if __name__=="__main__":
	argparser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
	argparser.add_argument('zipcode',help = '')
	sortorder_help = """
    available sort orders are :
    newest : Latest property details,
    cheapest : Properties with cheapest price
    """
	argparser.add_argument('sort',nargs='?',help = sortorder_help,default ='Homes For You')
	args = argparser.parse_args()
	zipcode = args.zipcode
	sort = args.sort
	print ("Fetching data for %s"%(zipcode))
	scrapedData = parse(zipcode,sort)
	print ("Writing data to output file")
	with open("properties-%s.csv"%(zipcode),'wb')as csvfile:
		fieldNames = ['title','address','city','state','postal_code','price','facts and features','real estate provider','url']
		writer = csv.DictWriter(csvfile, fieldNames = fieldNames)
		writer.writeheader()
		for row in  scrapedData:
			writer.writerow(row)
