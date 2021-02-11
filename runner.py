import os 
import sys
from datetime import date
import argparse
from media_config import media_config

parser = argparse.ArgumentParser(description='Enter start and end dates. Add media name to scrap certain site.')

parser.add_argument("date_start", help='start date of scrapping in YYYY-MM-DD format',
								type= date.fromisoformat)
parser.add_argument("date_end", help='end date of scrapping in YYYY-MM-DD format',
								type= date.fromisoformat)
# parser.add_argument("table_name", help='table name you want to save data to')
parser.add_argument("--media", help='name of spesific media to parse')

args = parser.parse_args()

if args.media:
	if args.media in media_config.keys():
		print('Scrapping ', args.media)
		command = "scrapy crawl media_scraper -a media={} -a date_start={} -a date_end={}".format(args.media,\
																					 		args.date_start, \
																					 		args.date_end)
		os.system(command)

	else:
		print(f'Media name "{args.media}" not in the list')
		print('Choose one of those:', media_config.keys())
else:
	for media in media_config.keys():
		print('Start scrapping ', media)
		command = "scrapy crawl media_scraper -a media={} -a date_start={} -a date_end={}".format(media, \
																								args.date_start,\
																								 args.date_end)
		os.system(command)
       