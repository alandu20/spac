import feedparser
from lxml import html
import pandas as pd
import requests

def main():
	df_spacs = pd.read_csv('data/spac_list_current.csv')
	df_spacs['formatted_ticker'] = 'NASDAQ: ' + df_spacs['Ticker']

	rss_feed = feedparser.parse('https://www.globenewswire.com/RssFeed/orgclass/1/feedTitle/'
		                        'GlobeNewswire%20-%20News%20about%20Public%20Companies')
	for entry in rss_feed.entries:
		page = requests.get(entry['id'])
		tree = html.fromstring(page.content)
		body_paragraphs = tree.xpath('//span[@class="article-body"]//p/text()')
		body = ' '.join(body_paragraphs)

		for formatted_ticker in df_spacs['formatted_ticker']:
			if formatted_ticker in body:
				print('Article for {} found...'.format({formatted_ticker}))
				print('time:', entry['published'])
				print('title:', entry['title'])
				print('url:', entry['id'], '\n')
	print('Searched all {} posts'.format(len(rss_feed.entries)))

if __name__ == "__main__":
    main()