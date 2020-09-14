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

from media_config import media_config
from utils import get_media_urls_for_period, get_media_url, get_clean_text, get_clean_time, parse_date

from scrapy.utils.project import get_project_settings


def p(message, title=''):
    print(f'================{title}==================')
    print(message)
    print('=========================================')


class MediaSpider(scrapy.Spider):
    # handle_httpstatus_list = [302]
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
        # не має залежити від списку ЗМІ що обробляється через перехресні посилання як у УП та ЄП
        sql_query = 'SELECT link FROM news_items'
        cursor.execute(sql_query)
        fetched_records = cursor.fetchall()
        records = []

        for record in fetched_records:
            records.append(record[0])

        return records

    def start_requests(self):
        urls_to_skip = self.get_previously_fetched_urls()

        for media in media_config.keys():
            config = media_config[media]

            if media != '112':
                continue

            date_start = datetime(2020, 8, 1)
            date_end = datetime(2020, 8, 31)

            page_number = 1

            urls_dates = ()

            if config.get('start_request_type') == 'pages_scraper':
                if media == 'svoboda':
                    # у свободы только одна дата и єто должна біть конечная дата
                    urls_dates = (
                        [get_media_url(media,
                                       date_end=date_end,
                                       page_number=page_number)],
                        [date_start]
                    )
                else:
                    urls_dates = (
                        [get_media_url(media,
                                       date=date_start,
                                       date_end=date_end,
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

            p(urls_dates)

            for url, date in zip(*urls_dates):
                yield scrapy.Request(
                    url=url,
                    callback=self.parse_article_headers,
                    meta={
                        'media': media,
                        'date': date,
                        'date_end': date_end,
                        'page_number': page_number,
                        'urls_to_skip': urls_to_skip,
                        # для медія в яких у артиклів немає дати, а є тільки дата на сторінки, і то тільки на межі днів
                        # наприклад https://hromadske.ua/news
                        'current_date': datetime.now(),
                    }
                )

    def parse_article_headers(self, response):
        media = response.meta['media']
        config = media_config[media]
        selectors = config['selectors']

        date_start = response.meta['date']
        date_end = response.meta['date_end']

        # TODO rename main_container to article_item
        all_articles = response.css(selectors['main_container'])

        count = 0

        # spec case for hromadske!!!! generalize!!
        current_date = response.meta['current_date']
        for article in all_articles:
            # count += 1
            # if count > 2:
            #     return

            # TODO треба винести поза цикл бо ця перевірка не залежить від article
            # СХОЖЕ що тут є проблема коли сторінка вміщує новини за 2 дні (межа днів):
            # в такому випадку новини попереднього дня будуть зберігатися як новини наступного
            # TODO перевырити після починки пагінатора
            if media == 'hromadske':  # or media == 'espreso':
                date_headers = response.css(selectors['date_header']).extract()

                article_date = current_date
                if len(date_headers) > 0:
                    date_header = date_headers[0]
                    article_date = parse_date(media, date_header)
                    current_date = article_date

            else:
                if selectors.get('date') != None:
                    article_dirty_date_str = article.css(
                        selectors['date']).extract()
                    p(article_dirty_date_str)
                    article_clean_date_str = get_clean_text(
                        article_dirty_date_str)
                    article_date = parse_date(media, article_clean_date_str)
                    p('!!!!!!!!!!!!!!!!!!!!HERE')
                    p(article_date)

                else:
                    article_date = date_start

            p(f'ARTICLE DATE IS: {article_date}')

            if not article_date:
                print('article_date is None: skipping the item')
                continue

            if article_date.date() > date_end.date():
                print(
                    f'article_date {article_date.date()} is BIGGER than date_end {date_end.date()}: skipping the item')
                continue

            if article_date.date() < date_start.date():
                print(
                    f'article_date {article_date.date()} is LESS than date_start {date_end.date()}: finishing')
                return

            # ---------- COLLECT ALL ITEMS --------------
            if date_start.date() <= article_date.date() <= date_end.date():
                print(
                    f'article_date {article_date.date()} is in range [{date_start.date()}, {date_end.date()}]')

                # ---LINK
                article_href = article.css(selectors['link']).extract_first()
                if 'http' in article_href:
                    article_url = article_href
                else:
                    article_url = config.get('url_prefix') + article_href

                # ---check whether this link`s been already parsed
                if article_url in response.meta['urls_to_skip']:
                    p('ALREADY IN DB')
                    continue

                article_loader = ItemLoader(
                    item=MediaScraperItem(),
                    selector=article
                )
                article_loader.add_value('link', article_url)
                # ---DATE
                article_loader.add_value('date', article_date)

                # ---DOMAIN
                article_loader.add_value(
                    'domain', config.get('domain'))

                # ---TITLE
                title_text_dirty_list = article.css(
                    selectors['title']).extract()
                title_clean = get_clean_text(title_text_dirty_list)
                article_loader.add_value('title', title_clean)

                # ---SUBTITLE
                if selectors.get('subtitle') != None:
                    subtitle_text_list = article.css(
                        selectors['subtitle']).extract()
                    subtitle = get_clean_text(subtitle_text_list)
                    article_loader.add_value('subtitle', subtitle)

                # ---TIME
                if selectors.get('time') != None:
                    time_text = article.css(selectors['time']).extract()
                    p(time_text)
                    time_parsed = get_clean_time(time_text)
                    p(time_parsed)
                    article_loader.add_value('time', time_parsed)

                # ---VIEWS
                if selectors.get('views') != None:
                    views_list = article.css(
                        selectors['views']).extract()

                    if media == "ukranews":
                        views = views_list[-1]
                    else:
                        views = get_clean_text(views_list)
                        # TODO extract to utility function get_views(media, dirty_value)
                        # it is supposed that media specific formatting is moved to media_config
                        if 'т' in views:
                            views = views.replace(' ', '')
                            if '.' in views:
                                views = views.replace('.', '')
                                views = views.replace('т', '00')
                            if ',' in views:
                                views = views.replace(',', '')
                            views = views.replace('т', '00')

                    article_loader.add_value('views', views)

                yield scrapy.Request(
                    url=article_url,
                    callback=self.parse_article_body,
                    meta={
                        'media': media,
                        'article_loader': article_loader
                    }
                )

        # після перебору всіх артиклів перевіряємо чи потрібно йти на наступну сторінку
        # TODO схоже принаймні для еспресо (знайти виключення!!) можна просто брати href з кнопки
        if selectors.get('next_page') != None:
            # TODO схоже що можно позбутися спец кейсу якщо завжди брати ОСТАННІЙ елемент next_page
            if media == 'espreso':
                last_next_page_btn = response.css(
                    selectors['next_page'])[-1]
                next_page_button_url = last_next_page_btn.extract()
            else:
                next_page_button_url = response.css(
                    selectors['next_page']).extract_first()
                if 'http' in next_page_button_url:
                    next_page_url = next_page_button_url
                else:
                    next_page_url = config.get(
                        'url_prefix') + next_page_button_url

            if next_page_button_url == None or next_page_button_url == 'javascript:;':
                return

            p(f"NEXT BUTTON URL: {next_page_button_url}")

            current_page_number = response.meta.get('page_number')

            # next_page_url = get_media_url(
            #     media,
            #     date=date_start,
            #     date_end=date_end,
            #     page_number=current_page_number+1
            # )

            p(f"next_page_url: {next_page_url}")
            new_meta = response.meta.copy()

            new_meta['page_number'] = current_page_number + 1
            new_meta['current_date'] = current_date

            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_article_headers,
                meta=new_meta,
            )

    def parse_article_body(self, response):
        media = response.meta['media']
        selectors = media_config[media]['selectors']
        text = response.css(selectors['text']).extract_first()

        # text може бути None, коли у стрічці новин посилання на підсайти з іншою версткою (типу лайфстайл, спорт, і т.д.)
        # або коли новина складається тільки з відео
        if text == None:
            p("SKIP BECAUSE TEXT IS NONE")
            return

        article_loader = response.meta['article_loader']

        article_loader.add_value('text', text)

        yield article_loader.load_item()
