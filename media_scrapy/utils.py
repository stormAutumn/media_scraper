
import re

# def get_whole_url(link):
#     if not "http" in link:
#         return "https://www.pravda.com.ua" + link
#     return link


def strip_text(text):
    text = re.sub(r"\s{2,}|\n|\s+$", "", text)
    text = text.strip()
    # text = text.strip()
    if not text:
        return None
    return text
    '112': {
        'domain': 'https://www.pravda.com.ua',
        'url_template': 'https://ua.112.ua/archive/p2?date_from={date}&date_to={date}&guest_and_news=&category=&type='
    },
    'svoboda': {
        'domain': 'https://www.epravda.com.ua',
        'url_template': 'https://www.radiosvoboda.org/z/630/{date}',
        'selectors': {
            'main_container': 'div.row>ul>li',
            'title': 'div.media-block > a::attr(title)',
            # 'subtitle': 'div.media-block > p.perex perex--mb perex--size-3::text',
            'link': 'div.media-block > a::attr(href)',
            'date': 'div.media-block span.date ::text'
        }
    },
    'znaj': {
        'domain': 'znaj.ua',
        'url_template': 'https://znaj.ua/news?page=335',
        'selectors': {
            'main_container': 'div.col-lg-8.col-sm-12 > a',
            'title': 'div.b-card--caption > h4::text',
            'subtitle': 'div.b-card--caption > h5::text',
            'link': '::attr(href)',
            'time': 'div.b-card--caption > time::text',
            'next_page': 'ul.pagination > li.page-item > a::attr(href)'
        }
    },
