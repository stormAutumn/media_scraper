import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from w3lib.html import replace_escape_chars
from scrapy.loader.processors import MapCompose
from media_scrapy.items import MediaScraperItem
from datetime import datetime
import dateparser
from scrapy.utils.project import get_project_settings
import psycopg2

from media_config import media_config, get_media_key_url, get_url_with_domain
from get_date import get_media_urls_for_period, get_media_url
from parse_date import parse_date


def p(message):
    print('=========================================')
    print(message)
    print('=========================================')


class PagesScrapy(scrapy.Spider):
    name = 'pages_scraper'

    def get_previously_fetched_urls(self):
        settings = get_project_settings()
        db_settings = settings.getdict("DB_SETTINGS")
        if not db_settings:
            raise NotConfigured

        conn = psycopg2.connect(dbname=db_settings['db'],
                                user=db_settings['user'],
                                password=db_settings['passwd'],
                                host=db_settings['host'])
        cursor = conn.cursor()

        sql_query = "SELECT link FROM news_items"
        cursor.execute(sql_query)
        fetched_records = cursor.fetchall()
        records = []
        for record in fetched_records:
            records.append(record[0])
        return records

    def start_requests(self):

        urls_to_skip = self.get_previously_fetched_urls()

        for media, media_dict in media_config.items():
            if media != 'liga':
                continue

            date = datetime(2020, 2, 1)
            date_end = datetime(2020, 5, 31)
            page_number = 1

            start_urls = get_media_urls_for_period(
                media, date, date_end=date_end, page_number=page_number)
            p('~~~~~~~~~~~~~~~~START URL```````````````')

            if media == 'svoboda':
                # у свободы ПОКА только одна дата и єто должна біть конечная дата
                start_url = get_media_url(
                    media,
                    date=date_end,
                    page_number=page_number
                )

            yield scrapy.Request(
                url=start_url,
                callback=self.parse_article_headers,
                meta={
                    'date': date,
                    'date_end': date_end,
                    'page_number': page_number,
                    'urls_to_skip': urls_to_skip
                }
            )

    def parse_article_headers(self, response):
        media_key = get_media_key_url(response.request.url)
        config = media_config.get(media_key, {})
        media_selectors = config.get('selectors')

        date_start = response.meta['date']
        date_end = response.meta['date_end']

        articles = response.css(media_selectors.get('main_container'))

        count = 0
        for article in articles:
            # count += 1
            # if count > 10:
            #     return

            if media_key == 'hromadske':
                date_header = response.css(
                    media_selectors.get('date_header')).extract_first()
                if date_header != None:
                    article_date = dateparser.parse(date_header, date_formats=[
                        '%d %B'], languages=['uk'])

                    p(f'ARTICLE DATE IS {article_date}')
                else:
                    continue

            else:
                article_date_text = articles.css(
                    media_selectors.get('date')).extract_first()

            article_date = parse_date(media_key, article_date_text)
            p('ARTICLE DATE')
            p(article_date)

            if article_date.date() > date_end.date():
                print(
                    f'article_date {article_date.date()} is BIGGER than date_end {date_end.date()}')
                continue

            if date_start.date() <= article_date.date() <= date_end.date():
                print(
                    f'article_date {article_date.date()} is in range [{date_start.date()}, {date_end.date()}]')

                article_loader = ItemLoader(
                    item=MediaScraperItem(),
                    selector=article
                )

                article_loader.add_value('date', article_date)

                article_loader.add_value(
                    'domain', config.get('domain'))

                title_text = article.css(
                    media_selectors.get('title')).extract_first()
                title_stripped = title_text.strip()
                title = title_stripped.replace('\n,', '')
                p(title)

                article_loader.add_value('title', title)

                article_href = article.css(
                    media_selectors.get('link')).extract_first()

                if 'http' in article_href:
                    article_url = article_href
                else:
                    article_url = config.get('url_prefix') + article_href

                if article_url in response.meta['urls_to_skip']:
                    p(article_url + '         ====================    есть в базе')
                    continue

                article_loader.add_value('link', article_url)

                if media_selectors.get('subtitle') != None:
                    article_loader.add_css(
                        'subtitle', media_selectors.get('subtitle'))

                if media_selectors.get('time') != None:
                    time_text = article.css(
                        media_selectors.get('time')).extract()
                    time_string = ''.join(time_text)
                    t = time_string.replace(',', '')
                    time = t.replace('\n', '')
                    time_stripped = time.strip()
                    # p(time_stripped)
                    time_parsed = datetime.strptime(
                        time_stripped, "%H:%M").time()
                    article_loader.add_value('time', time_parsed)

                if media_selectors.get('views') != None:
                    article_loader.add_css(
                        'views', media_selectors.get('views'))

                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article_body,
                    meta={'article_loader': article_loader}
                )

            else:
                print(
                    f'article_date {article_date.date()} is LESS than date_end {date_end.date()}')
                return

        if media_key == 'svoboda' or media_key == 'politeka' or media_key == 'interfax' or media_key == 'hromadske' or media_key == 'censor':
            # p(media_key)
            current_page_number = response.meta.get('page_number')
            # у свободы ПОКА только одна дата и єто должна біть конечная дата
            next_page_url = get_media_url(
                media_key,
                date=date_end,
                page_number=current_page_number+1
            )

            new_meta = response.meta.copy()
            new_meta['page_number'] = current_page_number + 1
            # p(new_meta)

            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_article_headers,
                meta=new_meta,
            )

        elif media_key == 'strana':
            next_page_button_url = response.css(
                media_selectors.get('next_page')).extract_first()
            p(next_page_button_url)

            if next_page_button_url != None:
                current_page_number = response.meta.get('page_number')

                next_page_url = get_media_url(
                    media_key,
                    date=date_end,
                    page_number=current_page_number+1)

                p(next_page_url)

                new_meta = response.meta.copy()
                new_meta['page_number'] = current_page_number + 1

                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse_article_headers,
                    meta=new_meta,
                )
        elif media_key == 'liga':
            next_page_button_url = response.css(
                media_selectors.get('next_page')).extract_first()
            p(next_page_button_url)

            if next_page_button_url != None and 'page' in next_page_button_url:
                current_page_number = response.meta.get('page_number')
                next_page_url = get_media_url(
                    media_key,
                    date=date_end,
                    page_number=current_page_number+1)

                p(next_page_url)

                new_meta = response.meta.copy()
                new_meta['page_number'] = current_page_number + 1

                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse_article_headers,
                    meta=new_meta,
                )

        else:
            next_page_button_url = response.css(
                media_selectors.get('next_page')).extract_first()
            if next_page_button_url != None:
                next_page_url = config.get('url_prefix') + next_page_button_url

                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse_article_headers,
                    meta=response.meta.copy(),)

    def parse_article_body(self, response):
        media_key = get_media_key_url(response.request.url)
        config = media_config.get(media_key, {})
        media_selectors = config.get('selectors')
        text = response.css(media_selectors.get('text')).extract_first()

        article_loader = response.meta['article_loader']

        article_loader.add_value('text', text)
        yield article_loader.load_item()
