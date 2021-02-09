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
from functools import reduce

from media_config import media_config
from utils import get_media_urls_for_period, get_media_url, get_clean_text,\
                    get_clean_time, parse_date, parse_date_from_article_page,\
                    get_clean_views, get_categories_string

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

            date_start = datetime(2020, 12, 1)
            date_end = datetime(2020, 12, 31)

            page_number = 1

            # для vgolos будемо передавати не номер сторінки, а offset, тож треба починати з 0:
            if media == 'vgolos':
                page_number = 0

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

        current_date = response.meta['current_date']

        # газета по-українськи в своєму API повертає html сторінки в json
        # до того ж json якийсь неправильний і його спочатку треба очистити
        if media == 'gazetaua':
            json_response = response.text.strip('RESTful.newsJsonpHandler();')
            json_response = json.loads(json_response)
            try:
                # body = scrapy.Selector(text=json_response['html'], type="html")
                response = response.replace(body = json_response['html'])

            except KeyError:
                print('Processed all pages: finishing')
                return

        # Зараз цей випадок тільки для Обозревателя
        # але якщо ще будуть такі медіа, то можна змінити їх тип на якийсь json_scraper
        elif config.get('response_type') == 'json_scraper':
            all_articles = json.loads(response.text)
            if selectors.get('main_container') != None:
                all_articles = all_articles[selectors.get('main_container')]
            if not all_articles or (not isinstance(all_articles,list)):
                print(f'Parsed all pages for {date_start}: finishing')
                return 
                
            for article_loader, article_url in self.parse_json_result(all_articles, selectors, config, media, response.meta['urls_to_skip']):
                if article_url:
                    if article_loader.get_collected_values('text'):
                        yield article_loader.load_item()
                    else:    
                        yield scrapy.Request(
                                url=article_url,
                                callback=self.parse_article_body,
                                meta={
                                    'media': media,
                                    'article_loader': article_loader
                                }
                            )

        else:
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

                if article_date.date() > date_end.date():
                    print(
                        f'article_date {article_date.date()} is BIGGER than date_end {date_end.date()}: skipping the item')
                    continue

                if article_date.date() < date_start.date():
                    print(
                        f'article_date {article_date.date()} is LESS than date_start {date_start.date()}: finishing')
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

            current_page_number = response.meta.get('page_number')
            next_page_number = current_page_number+1
            # не шукаємо урл на сторінці, а просто збільшуємо page_number
            if selectors.get('next_page') == 'next_number':
                # поки одиничний випадок для вголос, бо там в урлі офсет збільшується на 15
                # надалі можна буде додати це число в конфіг медіа, якщо ще будуть схожі
                if media == 'vgolos':
                    next_page_number = current_page_number+15
        
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
            p(response.url)
            return

        article_loader = response.meta['article_loader']

        # коли немає часу чи дата на основній сторінці може бути помилкова, отримуємо дату зі сторінки зі статтею
        if selectors.get('date_in_text') != None:
            date_from_text = response.css(selectors['date_in_text']).get()
            if date_from_text:
                date_from_text = parse_date_from_article_page(media, date_from_text)
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

        article_loader.add_value('text', text)


        # НВ і 24 канал беруть кількість переглядів з іншої сторінки, на яку ми тут переходимо
        # TODO: переписати це, додавши урл у конфіг
        if media == 'nv':
            views_url = response.url.rsplit('-', maxsplit=1)[-1]
            views_url = 'https://nv.ua/get_article_views/' + views_url
            new_meta = response.meta.copy()
            yield scrapy.Request(
                url=views_url,
                callback=self.get_nv_views,
                meta=new_meta,
            )
        elif media == '24tv':
            views_url = response.url.rsplit('_', maxsplit=1)[-1].strip('n')
            views_url = 'https://counter24.luxnet.ua/counter/' + views_url
            new_meta = response.meta.copy()
            yield scrapy.Request(
                url=views_url,
                callback=self.get_24tv_views,
                meta=new_meta,
            )
        else:
            yield article_loader.load_item()



    def get_nv_views(self, response):

        views = response.css('::text').get()
        article_loader = response.meta['article_loader']
        
        if views:
            article_loader.add_value('views', views)

        yield article_loader.load_item()


    def get_24tv_views(self, response):

        views = json.loads(response.text)
        if views and ('value' in views.keys()):
            views = views['value']
        article_loader = response.meta['article_loader']
        
        if views:
            article_loader.add_value('views', views)

        yield article_loader.load_item()


    def parse_json_result(self, all_articles, selectors, config, media, urls_to_skip):
        for article in all_articles:

            article_loader = ItemLoader(
            item=MediaScraperItem(),
            selector=article)

            # вибираємо з json потрібні значення
            article_url = None
            for key, selector in selectors.items():
                if isinstance(selector, list):
                    value = reduce((lambda seq, key: seq[key]), selector, article)

                    if key == 'link':
                        if 'http' not in value:
                            value = config.get('url_prefix') + value

                        if value in urls_to_skip:
                            p('ALREADY IN DB')
                            break
                        article_url = value

                    if key == 'date':
                        value = parse_date(media, value)

                    article_loader.add_value(key, value)
         
            article_loader.add_value('domain', config.get('domain'))


            yield article_loader, article_url
        


