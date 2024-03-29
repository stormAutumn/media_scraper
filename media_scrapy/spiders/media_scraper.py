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
import json
import xmltodict
from functools import reduce
import re


from media_config import media_config
from utils import get_media_urls_for_period, get_media_url, get_clean_text,\
                    get_clean_time, parse_date, parse_date_from_article_page,\
                    get_clean_views, get_categories_string

from scrapy.utils.project import get_project_settings


class OldDateError(Exception):
    """Class for exceptions when date is less then start date."""
    pass


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
        table = db_settings['table']
        # не має залежити від списку ЗМІ що обробляється через перехресні посилання як у УП та ЄП
        sql_query = 'SELECT link FROM {}'.format(table)
        cursor.execute(sql_query)
        fetched_records = cursor.fetchall()
        records = []

        for record in fetched_records:
            records.append(record[0])

        return records

    def start_requests(self):
        urls_to_skip = self.get_previously_fetched_urls()

        media = self.media
        date_start = self.date_start
        date_end = self.date_end

        config = media_config[media]

        print(date_start, date_end)
        
        page_number = 1

        if config.get('start_page_number') != None:
            page_number = config.get('start_page_number')

        urls_dates = ()

        if config.get('start_request_type') == 'pages_scraper':
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
        current_date = response.meta['current_date']
        try:
            for article in self.process_articles(response, config):
                article_url = article[0]
                article_loader = article[1]
                if len(article) == 3:
                    current_date = article[2]
                if article_url:
                    if article_loader.get_collected_values('text'):
                        yield article_loader.load_item()
                    else:    
                        yield scrapy.Request(
                                url=article_url,
                                callback=self.parse_article_body,
                                meta={
                                    'media': media,
                                    'config': config,
                                    'article_loader': article_loader,
                                    'date_start': date_start,
                                    'date_end': date_end
                                }
                            )
        except OldDateError as error:
            print(error)
            return

        # після перебору всіх артиклів перевіряємо чи потрібно йти на наступну сторінку
        # TODO схоже принаймні для еспресо (знайти виключення!!) можна просто брати href з кнопки
        if selectors.get('next_page') != None:  

            current_page_number = response.meta.get('page_number')
            next_page_number = current_page_number+1
            # не шукаємо урл на сторінці, а просто збільшуємо page_number
            if selectors.get('next_page') == 'next_number':
                # поки одиничний випадок для вголос, бо там в урлі офсет збільшується на 15
                # надалі можна буде додати це число в конфіг медіа, якщо ще будуть схожі
                if media == 'vgolos':
                    next_page_number = current_page_number+15
        
                if (media == 'svoboda') and current_page_number==100:
                    date_end = current_date
                    next_page_number = 0

                next_page_url = get_media_url(
                    media,
                    date=date_start,
                    date_end=date_end,
                    page_number=next_page_number
                )

            else:
                next_page_button_url = response.css(
                    selectors['next_page']).extract_first()

                if next_page_button_url == None or next_page_button_url == 'javascript:;':
                    return

                if 'http' in next_page_button_url:
                    next_page_url = next_page_button_url
                else:
                    next_page_url = config.get(
                        'url_prefix') + next_page_button_url

                

                p(f"NEXT BUTTON URL: {next_page_button_url}")

            p(f"next_page_url: {next_page_url}")
            new_meta = response.meta.copy()
            new_meta['page_number'] = next_page_number
            new_meta['current_date'] = current_date
            new_meta['date_end'] = date_end

            yield scrapy.Request(
                url=next_page_url,
                callback=self.parse_article_headers,
                meta=new_meta,
            )


    def process_articles(self, response, config):
        if config.get('response_type') == 'xml_scraper':
            yield from self.parse_xml_response(response, config)
        elif config.get('response_type') == 'json_scraper':
            yield from self.parse_json_response(response, config) 
        else:
            yield from self.parse_html_response(response, config)


    def parse_html_response(self, response, config):
        media = response.meta['media']
        selectors = config['selectors']
        date_start = response.meta['date']
        date_end = response.meta['date_end']
        current_date = response.meta['current_date']

        # газета по-українськи в своєму API повертає html сторінки в json
        # до того ж json якийсь неправильний і його спочатку треба очистити
        if media == 'gazetaua':
            json_response = response.text.strip('RESTful.newsJsonpHandler();')
            json_response = json.loads(json_response)
            try:
                response = response.replace(body = json_response['html'])
            except KeyError:
                print('Processed all pages: finishing')
                return

        # TODO rename main_container to article_item
        all_articles = response.css(selectors['main_container'])         

        if not all_articles:
            print('No articles on page: finishing')
            return

        # if media has no date selector - all articles on page have same date
        if not selectors.get('date'):
            article_date = date_start

        # spec case for hromadske and espreso!!!! generalize!!
        # СХОЖЕ що тут є проблема коли сторінка вміщує новини за 2 дні (межа днів):
        # в такому випадку новини попереднього дня будуть зберігатися як новини наступного
        # TODO перевырити після починки пагінатора
        if selectors.get('date_header') != None:
            date_headers = response.css(selectors['date_header']).extract()

            article_date = current_date
            if len(date_headers) > 0:
                date_header = date_headers[0]
                article_date = parse_date(media, date_header)
                current_date = article_date

        # перевіряємо дату останньої статті на сторінці
        # якщо вона надто свіжа - переходимо на наступну сторінку
        if (config.get('start_request_type') == 'pages_scraper') and (selectors.get('date') != None):
            last_date = all_articles[-1].css(selectors['date']).extract()
            last_date = parse_date(media, get_clean_text(last_date))
            p(last_date)
            if last_date.date() > date_end.date():
                print('All news on page are too new: GO TO NEXT PAGE')
                all_articles = []

        for article in all_articles:
            # count += 1
            # if count > 2:
            #     return
           
            if selectors.get('date') != None:
                article_dirty_date_str = article.css(
                    selectors['date']).extract()
                p(article_dirty_date_str)
                article_clean_date_str = get_clean_text(
                    article_dirty_date_str)
                article_date = parse_date(media, article_clean_date_str)
                p(article_date)


            p(f'ARTICLE DATE IS: {article_date}')

            if not article_date:
                print('article_date is None: skipping the item')
                continue

            current_date = article_date

            if article_date.date() > date_end.date():
                print(
                    f'article_date {article_date.date()} is BIGGER than date_end {date_end.date()}: skipping the item')
                continue

            if article_date.date() < date_start.date():
                # print(
                #     f'article_date {article_date.date()} is LESS than date_start {date_start.date()}: finishing')
                raise OldDateError(f'article_date {article_date.date()} is LESS than date_start {date_start.date()}: finishing')
                # (Exception(f'article_date {article_date.date()} is LESS than date_start {date_start.date()}: finishing'))

            # ---------- COLLECT ALL ITEMS --------------
            if date_start.date() <= article_date.date() <= date_end.date():
                print(
                    f'article_date {article_date.date()} is in range [{date_start.date()}, {date_end.date()}]')

                # ---LINK
                article_href = article.css(selectors['link']).extract_first()

                if not article_href:
                    print('Link is None: skipping the item')
                    continue

                if 'http' in article_href:
                    article_url = article_href
                else:
                    article_url = config.get('url_prefix') + article_href

                if media=='zik':
                    article_url = article_url.replace('http:', 'https:')

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

                # ---category
                if selectors.get('category') != None:
                    category_text = article.css(selectors['category']).extract()
                    if category_text:
                        p(category_text)
                        category = get_categories_string(category_text)
                        article_loader.add_value('category', category)

                # ---VIEWS
                if selectors.get('views') != None:
                    views_list = article.css(
                        selectors['views']).extract()
                    if views_list:
                        views = get_clean_views(media, views_list)
                        
                        article_loader.add_value('views', views)
                
                yield article_url, article_loader, current_date
               

    def parse_json_response(self, response, config):
        selectors = config['selectors']
    
        all_articles = json.loads(response.text)
        if selectors.get('main_container') != None:
            all_articles = all_articles[selectors.get('main_container')]
        if not all_articles or (not isinstance(all_articles,list)):
            print(f'Parsed all pages for {response.meta.date}: finishing')
            return 
                
        for article in all_articles:

            article_loader = ItemLoader(
            item=MediaScraperItem(),
            selector=article)

            article_loader.add_value('domain', config.get('domain'))

            # вибираємо з json потрібні значення
            article_url = None
            for key, selector in selectors.items():
                if isinstance(selector, list):
                    value = reduce((lambda seq, key: seq[key]), selector, article)

                    if key == 'link':
                        if 'http' not in value:
                            value = config.get('url_prefix') + value

                        if value in response.meta['urls_to_skip']:
                            p('ALREADY IN DB')
                            break
                        article_url = value

                    if key == 'date':
                        value = parse_date(response.meta['media'], value)

                    article_loader.add_value(key, value)

            yield article_url, article_loader


    def parse_xml_response(self, response, config):
        selectors = config['selectors']
        all_articles = reduce(lambda seq, key: seq[key], selectors.get('main_container'), \
                                xmltodict.parse(response.text))

        for article in all_articles:
            article_url = article[selectors.get('link')]

            article_loader = ItemLoader(
                    item=MediaScraperItem(),
                    selector=article
                )

            article_loader.add_value('link', article_url)
            article_loader.add_value('domain', config.get('domain'))

            yield article_url, article_loader


    def parse_article_body(self, response):
        media = response.meta['media']
        config = response.meta['config']
        selectors = config['selectors']
        date_start = response.meta['date_start']
        date_end = response.meta['date_end']

        text = response.css(selectors['text']).extract_first()
        
        # text може бути None, коли у стрічці новин посилання на підсайти з іншою версткою (типу лайфстайл, спорт, і т.д.)
        # або коли новина складається тільки з відео
        if text == None:
            p("SKIP BECAUSE TEXT IS NONE")
            p(response.url)
            return

        article_loader = response.meta['article_loader']

        # коли немає часу чи дата на основній сторінці може бути помилкова, отримуємо дату зі сторінки зі статтею
        if selectors.get('date_in_text') != None:
            date_from_text = response.css(selectors['date_in_text']).get()
            if date_from_text:
                date_from_text = parse_date_from_article_page(media, date_from_text)
                if date_from_text.date() < date_start.date() or date_from_text.date() > date_end.date():
                    p(f"Article date {date_from_text.date()} is NOT in range [{date_start.date()}, {date_end.date()}]")
                    return
                article_loader.replace_value('date', date_from_text)

        if selectors.get('category_in_text') != None:
            category = response.css(selectors['category_in_text']).extract()
            if category:
                category = get_categories_string(category)
                article_loader.add_value('category', category)

        if selectors.get('views_in_text') != None:
            views = response.css(selectors['views_in_text']).extract()
            if views:
                views = get_clean_views(media, views)
                article_loader.add_value('views', views)

        if selectors.get('subtitle_in_text') != None:
            subtitle = response.css(selectors['subtitle_in_text']).get()
            if subtitle:
                subtitle = subtitle.strip()
                article_loader.add_value('subtitle', subtitle)

        if selectors.get('title_in_text') != None:
            title = response.css(selectors['title_in_text']).get()
            if title:
                title = title.strip()
                article_loader.replace_value('title', title)

        article_loader.add_value('text', text)


        # якщо є окрема сторінка з кількістю переглядів, переходимо на неї 
        if config.get('views_url'):
            article_id_pattern = re.compile(config.get('article_id_pattern'))
            article_id = article_id_pattern.search(response.url).group(1)
            views_url = config.get('views_url') + article_id
            new_meta = response.meta.copy()
            yield scrapy.Request(
                url=views_url,
                callback=self.parse_views_page,
                meta=new_meta,
            )
        else:
            yield article_loader.load_item()


    def parse_views_page(self, response):
        views = None
        media = response.meta['media']
        if media == 'nv':
            views = response.css('::text').get()
        elif media == '24tv':
            json_views = json.loads(response.text)
            if json_views and ('value' in json_views.keys()):
                views = json_views['value']

        article_loader = response.meta['article_loader']

        if views:
            article_loader.add_value('views', views)

        yield article_loader.load_item()
        