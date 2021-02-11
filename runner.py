import os 
import sys
from datetime import datetime
import argparse
from media_config import media_config
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Enter start and end dates. Add media name to scrap certain site.')

	parser.add_argument("date_start", help='start date of scrapping in YYYY-MM-DD format',
									type= datetime.fromisoformat)
	parser.add_argument("date_end", help='end date of scrapping in YYYY-MM-DD format',
									type= datetime.fromisoformat)
	parser.add_argument("--media", help='name of spesific media to parse')

	args = parser.parse_args()
	configure_logging()
	runner = CrawlerRunner(get_project_settings())

	if args.media:
		if args.media in media_config.keys():
			print('Scrapping', args.media)
			runner.crawl('media_scraper', media=args.media, date_start=args.date_start, date_end=args.date_end)
			reactor.run()
		else:
			print(f'Media name "{args.media}" not in the list')
			print('Choose one of those:', media_config.keys())
	else:
		@defer.inlineCallbacks
		def crawl():
			for media in media_config.keys():
				print('Start scrapping', media)
				yield runner.crawl('media_scraper', media=media, date_start=args.date_start, date_end=args.date_end)
			reactor.stop()

		crawl()
		reactor.run()




