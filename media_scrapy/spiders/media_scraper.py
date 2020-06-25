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
import psycopg2
from bs4 import BeautifulSoup


from media_config import media_config, get_media_key_url, get_url_with_domain
from get_date import get_media_urls_for_period, get_media_url
from scrapy.utils.project import get_project_settings
from parse_date import parse_date


def p(message):
    print('=========================================')
    print(message)
    print('=========================================')


class MediaSpider(scrapy.Spider):
    name = 'media_scraper'

    # TODO: move to utils
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
        # TODO має залежити від списку ЗМІ що обробляється
        sql_query = "SELECT link FROM news_items"
        cursor.execute(sql_query)
        fetched_records = cursor.fetchall()
        records = []

        for record in fetched_records:
            records.append(record[0])

        return records

    def start_requests(self):
        urls_to_skip = self.get_previously_fetched_urls()

        for media in media_config.keys():
            if media != 'svoboda':
                continue

            date_start = datetime(2020, 6, 23)
            date_end = datetime(2020, 6, 24)
            page_number = 1

            config = media_config[media]

            urls_dates = ()

            if config.get('spider') == 'pages_scraper':
                if media == 'svoboda':
                    # у свободы ПОКА только одна дата и єто должна біть конечная дата
                    urls_dates = (
                        [get_media_url(media,
                                       date=date_end,
                                       page_number=page_number)],
                        [date_end]
                    )
                else:
                    urls_dates = (
                        [get_media_url(media,
                                       date=date_start,
                                       page_number=page_number)],
                        [date_start]
                    )

            else:
                urls_dates = get_media_urls_for_period(
                    media,
                    date_start=date_start,
                    date_end=date_end,
                    page_number=page_number
                )

            for url, date in zip(*urls_dates):
                yield scrapy.Request(
                    url=url,
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

        # p(date_start)
        # p(date_end)
        # return
        articles = response.css(media_selectors.get('main_container'))

        count = 0
        for article in articles:
            # count += 1
            # if count > 5:
            #     return

            if media_key == 'hromadske' or media_key == 'espreso':
                date_header = response.css(
                    media_selectors.get('date_header')).extract_first()
                if date_header != None:
                    article_date = dateparser.parse(date_header, date_formats=[
                        '%d %B'], languages=['uk'])

                    # p(f'ARTICLE DATE IS {article_date}')
                else:
                    continue
            else:
                if media_selectors.get('date') != None:
                    article_date_text = articles.css(
                        media_selectors.get('date')).extract_first()

                    # p(article_date_text)

                    article_date = parse_date(media_key, article_date_text)
                    p(f'ARTICLE DATE IS: {article_date}')
                else:
                    date_response_format = response.meta['date'].strftime(
                        "%d.%m.%Y")
                    article_date = dateparser.parse(date_response_format, date_formats=[
                        '%d.%m.%Y'], languages=['uk'])
                    p(f'ARTICLE DATE IS: {article_date}')

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

            # ---------- COLLECT ALL ITEMS --------------

                # ---DOMAIN
                article_loader.add_value(
                    'domain', config.get('domain'))

                # ---TITLE
                title_text_list = article.css(
                    media_selectors.get('title')).extract()
                title_text = ''.join(title_text_list)
                title_stripped = title_text.strip()
                title = title_stripped.replace('\n,', '')
                article_loader.add_value('title', title)

                # ---LINK
                article_href = article.css(
                    media_selectors.get('link')).extract_first()
                # p(f'article_href is: {article_href}')
                if 'http' in article_href:
                    article_url = article_href
                else:
                    article_url = config.get('url_prefix') + article_href

                # p(f'article_url is: {article_url}')

                # --------check whether this link`s been already parsed
                if article_url in response.meta['urls_to_skip']:
                    # p(article_url + '         ====================    есть в базе')
                    continue

                article_loader.add_value('link', article_url)

                # ---DATE
                if media_selectors.get('date') != None:
                    date_response_format = article.css(
                        media_selectors.get('date')).extract_first()
                    article_date = parse_date(media_key, date_response_format)
                else:
                    date_response_format = response.meta['date'].strftime(
                        "%d.%m.%Y")
                    article_date = dateparser.parse(date_response_format, date_formats=[
                        '%d.%m.%Y'], languages=['uk'])

                article_loader.add_value('date', article_date)

                # ---SUBTITLE
                if media_selectors.get('subtitle') != None:
                    subtitle_text_list = article.css(
                        media_selectors.get('subtitle')).extract()

                    subtitle_text = ''.join(subtitle_text_list)

                    subtitle_stripped = subtitle_text.strip()
                    subtitle = subtitle_stripped.replace('\t,\n,', '')
                    article_loader.add_value('subtitle', subtitle)

                # ---TIME
                if media_selectors.get('time') != None:
                    time_text = article.css(
                        media_selectors.get('time')).extract()
                    p(media_selectors.get('time'))
                    time_string = ''.join(time_text)
                    t = time_string.replace(',', '')
                    time = t.replace('\n', '')
                    time_stripped = time.strip()
                    time_parsed = datetime.strptime(
                        time_stripped, "%H:%M").time()
                    article_loader.add_value('time', time_parsed)

                # --VIEWS
                if media_selectors.get('views') != None:
                    views = article.css(
                        media_selectors.get('views')).extract_first()
                    if 'т' in views:
                        if '.' in views:
                            views = views.replace('т', '00')
                            views = views.replace('.', '')
                        else:
                            views = views.replace('т', '000')
                    article_loader.add_value('views', views)
                    # p(views)

                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article_body,
                    meta={'article_loader': article_loader}
                )

            else:
                print(
                    f'article_date {article_date.date()} is LESS than date_end {date_end.date()}')
                return

        # ----------GETTING NEXT PAGE IF THERE IS SOME ------------------

        if media_selectors.get('next_page') != None:
            if media_key == 'espreso':
                next_page_button_url = response.css(
                    media_selectors.get('next_page'))[-1].extract()
            else:
                next_page_button_url = response.css(
                    media_selectors.get('next_page')).extract_first()

            p(next_page_button_url)

            if media_selectors.get('next_page_number') != None:
                if media_selectors.get('next_page_number') == 'only_page_number':
                    current_page_number = response.meta.get('page_number')

                    # у svoboda ПОКИ тільки одна дата и це має бути кінцева дата
                    next_page_url = get_media_url(
                        media_key,
                        date=date_end,
                        page_number=current_page_number+1
                    )
                    new_meta = response.meta.copy()

                    new_meta['page_number'] = current_page_number + 1

                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse_article_headers,
                        meta=new_meta,
                    )

            if media_selectors.get('next_page_number') == 'page_and_date':
                if next_page_button_url != None:
                    current_page_number = response.meta.get('page_number')
                    next_page_url = get_media_url(
                        media_key,
                        date=date_end,
                        page_number=current_page_number+1)
                    new_meta = response.meta.copy()
                    new_meta['page_number'] = current_page_number + 1
                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse_article_headers,
                        meta=new_meta,
                    )

            if media_key == 'liga':
                if next_page_button_url != None and 'page' in next_page_button_url:

                    p('GOING TO THE NEXT PAGE')
                    current_page_number = response.meta.get('page_number')
                    next_page_url = get_media_url(
                        media_key,
                        date=date_end,
                        page_number=current_page_number+1)

                    new_meta = response.meta.copy()
                    new_meta['page_number'] = current_page_number + 1

                    yield scrapy.Request(
                        url=next_page_url,
                        callback=self.parse_article_headers,
                        meta=new_meta,
                    )

# =================================== can`t get this moment
            # if next_page_button_url != None:
            #     if 'http' in next_page_button_url:
            #         next_page_url = next_page_button_url
            #     else:
            #         next_page_url = config.get(
            #             'url_prefix') + next_page_button_url

                # yield scrapy.Request(
                #     url=next_page_url,
                #     callback=self.parse_article_headers,
                #     meta=response.meta.copy(),)

# ---------- PARSE ARTICLE BODY ------------------

    def parse_article_body(self, response):
        media_key = get_media_key_url(response.request.url)
        config = media_config.get(media_key, {})
        media_selectors = config.get('selectors')
        text = response.css(media_selectors.get('text')).extract_first()

        article_loader = response.meta['article_loader']

        article_loader.add_value('text', text)
        yield article_loader.load_item()
