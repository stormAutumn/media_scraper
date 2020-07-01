import re

media_config = {
    'pravda': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.pravda.com.ua',
        'url_prefix': 'https://www.pravda.com.ua',
        'url_template': 'https://www.pravda.com.ua/archives/date_{date}',
        'selectors': {
            'main_container': 'div.news.news_all>div.article',
            'title': 'div.article__title > a::text',
            'subtitle': 'div.article__subtitle::text',
            'text': 'article.post>div.block_post>div.post_text',
            'link': 'div.article__title a::attr(href)',
            'time': 'div.article__time ::text'
        }
    },
    'epravda': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.epravda.com.ua',
        'url_prefix': 'https://www.epravda.com.ua',
        'url_template': 'https://www.epravda.com.ua/archives/date_{date}',
        'selectors': {
            'main_container': 'div.news_list>div.article.article_news',
            'title': 'div.article__title > a::text',
            'text': 'div.block_post>div.post__text',
            'subtitle': 'div.article__subtitle ::text',
            'link': 'div.article__title a::attr(href)',
            'time': 'div.article__time::text'
        }
    },
    'obozrevatel': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.obozrevatel.com',
        'url_prefix': '',
        'url_template': 'https://www.obozrevatel.com/ukr/main-item/{date}.htm',
        'selectors': {
            'main_container': 'div.section-news-title-img-text__wrap>article.news-title-img-text',
            'title': 'div.news-title-img-text__content>a.news-title-img-text__title::text',
            'text': 'div.main-col__left div.news-full__text.io-article-body',
            'subtitle': 'div.news-title-img-text__content>a.news-title-img-text__text::text',
            'link': 'div.news-title-img-text__content>a::attr(href)',
            'time': 'div.news-title-img-text__wrap-icon>time.news-title-img-text__date::text',
            'views': 'div.news-title-img-text__wrap-icon>span.icon-views::text'
        }
    },
    'rbc': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.rbc.ua',
        'url_prefix': '',
        'url_template': 'https://www.rbc.ua/ukr/archive/{date}',
        'selectors': {
            'main_container': 'div.news-feed-item > div.content-section > a',
            'title': '::text',
            'text': 'div.publication-sticky-container',
            'link': '::attr(href)',
            'time': 'span.time::text'
        }
    },
    'liga': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.liga.net',
        'url_prefix': '',
        'url_template': 'https://www.liga.net/archive/{date}/all/page/{page_number}',
        'selectors': {
            'main_container': 'div.archive-materials>div.news-col',
            'title': 'div.news-col.clearfix>ul>li>a::text',
            'text': 'div#news-text',
            'link': 'div.news-col.clearfix>ul>li>a::attr(href)',
            'date': 'div.news-col.clearfix>ul>li>div.time::text',
            'next_page': 'div.pages > a[title="Next page"]::attr(href)'
        }
    },
    'unian': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.unian.ua',
        'url_prefix': '',
        'url_template': 'https://www.unian.ua/news/archive/{date}',
        'selectors': {
            'main_container': 'div.col-md-8.pl0.col-sm-12.sm-prl0>div.publications-archive>div.gallery-item',
            'title': 'div.gallery-item.news-inline-item>a::text',
            'text': 'div.article-text',
            'link': 'div.gallery-item.news-inline-item>a::attr(href)',
            'date': 'div.gallery-item.news-inline-item>div.bottom>div.left>div.item.time::text'
        }
    },
    'LB': {
        'start_request_type': 'media_scraper',
        'domain': 'https://ukr.lb.ua',
        'url_prefix': '',
        'url_template': 'https://ukr.lb.ua/archive/{date}',
        'selectors': {
            'main_container': 'ul.lenta > li.item-news',
            'title': 'a::text',
            'text': 'article.material > div.header',
            'subtitle': '::text',
            'link': 'div.title > a::attr(href)',
            'date': 'time::attr(datetime)'
        }
    },
    # zik requires AUTOTHROTTLE_ENABLED = true and futher delays
    'zik': {
        'start_request_type': 'media_scraper',
        'domain': 'zik.ua',
        'url_prefix': 'https://zik.ua',
        'url_template': 'https://zik.ua/sitemap/2020/{date}?pg={page_number}',
        'selectors': {
            'main_container': 'div.b-archive-news-list > ul.news-list > li.news-list-item',
            'title': 'a::text',
            'text': 'article.article',
            'link': 'a::attr(href)',
            'time': 'time.time::text',
            'pages': 'ul.pagination-box > li.active > a::attr(href)',
            'next_page': 'div.b-archive-news-list > ul.pagination-box > li.active + li > a::attr(href)',
            'next_page_number': 'page_and_date'
        }
    },
    'segodnya': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.segodnya.ua/ua',
        'url_prefix': 'https://www.segodnya.ua',
        'url_template': 'https://www.segodnya.ua/ua/newsitemap/{date}.html',
        'selectors': {
            'main_container': 'a:nth-child(n+8)',
            'title': '::text',
            'text': 'article.article',
            'link': '::attr(href)'
        }
    },
    '24tv': {
        'start_request_type': 'media_scraper',
        'domain': '24tv.ua',
        'url_prefix': '',
        'url_template': 'https://24tv.ua/archive/{date}/',
        'selectors': {
            'main_container': 'ul.list>li>div.txt',
            'title': 'a::text',
            'text': 'article.article',
            'link': 'a::attr(href)',
            'subtitle': 'div.desc::text',
            'date': 'span.date_time::text'
        }
    },
    'tsn': {
        'start_request_type': 'media_scraper',
        'domain': 'tsn.ua',
        'url_prefix': '',
        'url_template': 'https://tsn.ua/archive/{date}',
        'selectors': {
            'main_container': 'article.h-entry.c-entry',
            'title': 'h4 > a::text',
            'text': 'div.c-main',
            'link': 'h4 > a::attr(href)',
            'subtitle': 'p > a::text',
            'date': 'div.c-post-info > time::attr(datetime)',
            # 'next_page': 'div.text-center > div.js-more::attr(data-source)',
        }
    },
    'gordonua': {
        'start_request_type': 'media_scraper',
        'domain': 'gordonua.com',
        'url_prefix': 'https://gordonua.com/ukr',
        'url_template': 'https://gordonua.com/ukr/news/archive/{date}.html',
        'selectors': {
            'main_container': 'div.row> div.span-8 > div.block > div.lenta > div.media > div.row > div.span-8',
            'title': 'div.lenta_head > a::text',
            'text': 'div.block.article',
            'subtitle': 'div.span-8 > div.a_description::text',
            'link': 'div.span-8 > div.lenta_head > a::attr(href)',
            'date': 'div.span-8 > div.for_data::text'
        }
    },
    'apostrophe': {
        'start_request_type': 'media_scraper',
        'domain': 'apostrophe.ua',
        'url_prefix': '',
        'url_template': 'https://apostrophe.ua/ua/archives/{date}',
        'selectors': {
            'main_container': 'div.entry_news',
            'title': 'div.entry_news > a > strong::text',
            'text': 'div.content',
            'subtitle': 'a > div.title_short::text',
            'link': 'a::attr(href)',
            'time': 'div.ni__date.lorange::text'
        }
    },
    'unn': {
        'start_request_type': 'media_scraper',
        'domain': 'www.unn.com.ua',
        'url_prefix': 'https://www.unn.com.ua',
        'url_template': 'https://www.unn.com.ua/uk/news/{date}',
        'selectors': {
            'main_container': 'div.h-news-feed > ul > li',
            'title': 'p.title > a::text',
            'text': 'div.b-news-holder',
            'link': 'p.title > a::attr(href)',
            'time': 'span.date::text',
            'next_page': 'div.b-page-selector-holder > ul >li.page_nav.next_page > a::attr(href)'
        }
    },
    'focus': {
        'start_request_type': 'media_scraper',
        'domain': 'focus.ua',
        'url_prefix': 'https://focus.ua',
        'url_template': 'https://focus.ua/news/{date}',
        'selectors': {
            'main_container': 'ol.uk-list > li',
            'title': 'div.uk-link-heading::text',
            'text': 'section.pub-body',
            'link': 'article.uk-position-relative > a.uk-link-toggle::attr(href)',
            'time': 'time.card-time span.time::text',
        }
    },
    'ukranews': {
        'start_request_type': 'pages_scraper',
        'domain': 'https://ukranews.com',
        'url_prefix': 'https://ukranews.com',
        'url_template': 'https://ukranews.com/archiv/date_from/{date}/date_to/{date_end}/page/{page_number}',
        'selectors': {
            'main_container': 'div#panel1>a',
            'title': 'span.tape_news__title::text',
            'text': 'div.article_content',
            'link': '::attr(href)',
            'date': 'div.text > div.tape_news__info > span.tape_news__date::text',
            'views': 'div.text > div.tape_news__info > span.tape_news__date::text',
            'next_page': 'ul.pagination > li.arrow:last-child > a::attr(href)'
        },
    },
    # у Свободы пока что умеем обрабатывать только 100 страниц
    'svoboda': {
        'start_request_type': 'pages_scraper',
        'domain': 'www.radiosvoboda.org',
        'url_prefix': 'https://www.radiosvoboda.org',
        'url_template': 'https://www.radiosvoboda.org/z/630/{date}?p={page_number}',
        'selectors': {
            'main_container': '.content-offset .row>ul>li',
            'title': 'div.media-block > a::attr(title)',
            'text': 'div.body-container',
            'link': 'div.media-block > a::attr(href)',
            'date': 'div.media-block span.date ::text',
            'next_page_number': 'only_page_number'
        }
    },
    '112': {
        #robots_obey = False in settings
        'start_request_type': 'media_scraper',
        'domain': '112.ua',
        'url_prefix': 'https://ua.112.ua',
        'url_template': 'https://ua.112.ua/archive/p2?date_from={date}&date_to={date}&guest_and_news=&category=&type=',
        'selectors': {
            'main_container': 'div.decs-list',
            'title': 'a::text',
            'text': 'article.article-content.page-cont',
            'link': 'a::attr(href)',
            'date': 'div > span::text',
            'time': 'div > span > time::text',
            'next_page': 'ul.pagination > li.next> a::attr(href)'
        }
    },
    'dzerkalo_tyzhnya': {
        'start_request_type': 'media_scraper',
        'domain': 'https://dt.ua/',
        'url_prefix': 'https://zn.ua',
        'url_template': 'https://zn.ua/ukr/all-news/date={date}/p{page_number}',
        'selectors': {
            'main_container': 'ul.news_list > li > a',
            'title': 'span.news_anounce > span.news_title::text',
            'subtitle': 'span.news_anounce > span.news_summary::text',
            'link': 'a::attr(href)',
            'text': 'div.article_body div.article_body',
            'time': 'span.news_date::text',
            'next_page': 'div.navigate > span.next>a::attr(href)',
            'next_page_number': 'page_and_date'
        }
    },
    'strana': {
        'start_request_type': 'media_scraper',
        'domain': 'strana.ua',
        'url_prefix': 'https://strana.ua',
        'url_template': 'https://strana.ua/archive/day={date}/page-{page_number}.html',
        'selectors': {
            'main_container': 'article.lenta-news.clearfix',
            'title': 'div > div.title > a::text',
            'text': 'div.article-content',
            'link': 'div > div.title > a::attr(href)',
            'date': 'div > time.date > span::text',
            'time': 'div > time.date::text',
            'next_page': 'div.pagination > ul.pagination-list > li.next.next_page > a[rel="next"]::attr(href)',
            'next_page_number': 'page_and_date'
        }
    },
    'znaj': {
        'start_request_type': 'pages_scraper',
        'domain': 'znaj.ua',
        'url_prefix': '',
        'url_template': 'https://znaj.ua/news?page={page_number}',
        'selectors': {
            'main_container': 'div.col-lg-8.col-sm-12 > a',
            'title': 'div.b-card--caption > h4::text',
            'text': 'div.col-lg-8.col-md-12',
            'subtitle': 'div.b-card--caption > h5::text',
            'link': '::attr(href)',
            'date': 'div.b-card--caption > time::text',
            'next_page': 'ul.pagination > li.page-item > a[rel="next"]::attr(href)'
        }
    },
    'ictv': {
        'start_request_type': 'pages_scraper',
        'domain': 'fakty.com.ua',
        'url_prefix': '',
        'url_template': 'https://fakty.com.ua/ua/news/page/{page_number}/',
        'selectors': {
            'main_container': 'div#all_news_page>ul>li',
            'title': 'a>div.tape_title_small::text',
            'text': 'div.news_single ',
            'link': 'a::attr(href)',
            'subtitle': 'a>div.category_tape_exerpt>p::text',
            'date': 'i.time::text',
            'next_page': 'nav.prev-next-posts>div.prev-posts-link>a::attr(href)'
        }
    },
    'politeka': {
        'start_request_type': 'pages_scraper',
        'domain': 'https://politeka.net/uk',
        'url_prefix': '',
        'url_template': 'https://politeka.net/uk/newsfeed?page={page_number}',
        'selectors': {
            'main_container': 'div.b_post.b_post--image-sm > div.b_post--media',
            'title': 'a > h4::text',
            'subtitle': 'div.b_post--description::text',
            'link': 'a::attr(href)',
            'text': 'div.col-lg-8.col-md-12 div.article-body',
            'date': 'div.b_post--date::text',
            'next_page': 'ul.pagination > li.page-item > a[rel="next"]::attr(href)',
            'next_page_number': 'only_page_number'
        }
    },
    'interfax': {
        'start_request_type': 'pages_scraper',
        'domain': 'https://ua.interfax.com.ua',
        'url_prefix': 'https://ua.interfax.com.ua',
        'url_template': 'https://ua.interfax.com.ua/news/latest-{page_number}.html',
        'selectors': {
            'main_container': 'div.articles-section-view > div.grid.article',
            'title': 'div.col-57 > h1.article-link-wrapper > a::text',
            'link': 'div.col-57 > h1.article-link-wrapper > a::attr(href)',
            'text': 'div.grid.content > div.col-23 div.article-content',
            'date': 'div.article-image-wrapper .article-time *::text',
            'next_page': 'div.pager > a:nth-child(2)::attr(href)',
            'next_page_number': 'only_page_number'
        }
    },
    'hromadske_radio': {
        'start_request_type': 'pages_scraper',
        'domain': 'https://hromadske.radio',
        'url_prefix': 'https://hromadske.radio',
        'url_template': 'https://hromadske.radio/news/page/{page_number}',
        'selectors': {
            'main_container': 'article > div.wrap2 > div.content',
            'title': 'a > div.caption::text',
            'link': 'a:nth-child(2)::attr(href)',
            'text': 'div.inner-content',
            'date': 'div.date > time:nth-child(1)::text',
            'time': 'div.date > time:nth-child(2)::text',
            'next_page': 'ul.pages > li.link.center.active + li > a::attr(href)'
        }
    },
    'hromadske': {
        'start_request_type': 'pages_scraper',
        'domain': 'https://hromadske.ua/',
        'url_prefix': 'https://hromadske.ua',
        'url_template': 'https://hromadske.ua/news?page={page_number}',
        'selectors': {
            'main_container': 'div.NewsPostList > a',
            'title': 'div.NewsPublicationCard-title::text',
            'link': '::attr(href)',
            'text': 'div.PostPreview-contentWrapper',
            # 'date': 'div.date > time:nth-child(1)::text',
            'time': 'div.NewsPublicationCard-time::text',
            'next_page': 'div.NewsPostList-loadMore> a::attr(href)',
            'next_page_number': 'only_page_number',
            'date_header': 'div.NewsPostList > div.DateHeader > span::text'
        }
    },
    'espreso': {
        'start_request_type': 'pages_scraper',
        'domain': 'espreso.tv',
        'url_prefix': 'https://espreso.tv',
        'url_template': 'https://espreso.tv/news?page={page_number}/',
        'selectors': {
            'main_container': 'div.news-list ul.list > li',
            'title': 'div.txt a::text',
            'link': 'a::attr(href)',
            'time': 'div.time::text',
            'text': 'div.article',
            'next_page': 'div.b_center_pager>ul.pager_list>li.arrow',
            'next_page_number': 'only_page_number',
            'date_header': 'div.news-list.big.time-stamp > h2::text'
        }
    },
    # цензор банить, якщо великий інтервал дат. збільшення time_out in setting doesn`t help
    'censor': {
        'start_request_type': 'pages_scraper',
        'domain': 'https://censor.net.ua',
        'url_prefix': '',
        'url_template': 'https://censor.net.ua/news/all/page/{page_number}/category/0/interval/5/sortby/date',
        'selectors': {
            'main_container': 'section.news article.item',
            'title': 'a::text',
            'subtitle': 'div.anounce > a::text',
            'link': 'div.anounce > a::attr(href)',
            'text': 'div.main',
            'date': 'time::attr(datetime)',
            'views': 'div.hit > span > span.info::text',
            'next_page': 'div.news_paging:nth-child(1)  a.pag_next::attr(href)',
            'next_page_number': 'only_page_number'
        }
    }
}
