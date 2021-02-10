import re

media_config = {
    'pravda': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.pravda.com.ua',
        'url_prefix': 'https://www.pravda.com.ua',
        'url_template': 'https://www.pravda.com.ua/archives/date_{date}/',
        'selectors': {
            'main_container': 'div.article_news_list',
            'title': 'div.article_content > div.article_header > a::text',
            'subtitle': 'div.article_content > div.article_subheader::text',
            'text': 'div.container_sub_post_news > article.post > div.block_post',
            'link': 'div.article_content a::attr(href)',
            'views_in_text': 'div.post_views::text',
            'time': 'div.article_time::text'
        }
    },
    'epravda': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.epravda.com.ua',
        'url_prefix': 'https://www.epravda.com.ua',
        'url_template': 'https://www.epravda.com.ua/archives/date_{date}/',
        'selectors': {
            'main_container': 'div.news_list>div.article.article_news',
            'title': 'div.article__title > a::text',
            'text': 'div.block_post>div.post__text',
            'subtitle': 'div.article__subtitle ::text',
            'link': 'div.article__title a::attr(href)',
            'time': 'div.article__time::text',
            'views_in_text': 'div.post__statistic>div.post__views::text'
        }
    },
    # Дістаємо дані із json через декілька вкладених рівнів, тому ключі по порядку занесені у список
    # зараз в обозревателя і свободи 'next_page': 'next_number' означає, що їх наступна сторінка
    # формується просто збільшенням page_number на 1
    'obozrevatel': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.obozrevatel.com',
        'url_template': 'https://www.obozrevatel.com/api/news/newslist/relatednews/pictureoftheday/?page={page_number}&date={date}&language=ua',
        'selectors': {
            'main_container': 'Data',
            'link': ['Localizations','ua','Url'],
            'title': ['Localizations','ua','Title'],
            'subtitle': ['Localizations','ua','Description'],
            'category': ['Section','Localizations','ua','Title'],
            'date': ['PublishDate'],
            'views': ['ViewCount'],
            'text': 'div.newsFull_text,div.news-full__text',
            'next_page': 'next_number'
        }
    },
    'rbc': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.rbc.ua',
        'url_prefix': '',
        'url_template': 'https://www.rbc.ua/ukr/archive/{date}',
        'selectors': {
            'main_container': 'div.newsline > div > a',
            'title_in_text': 'article>h1::text',
            'title': '::text',
            'text': 'div.publication-sticky-container,div.txt',
            'link': '::attr(href)',
            'time': 'span.time::text'
        }
    },
    'liga': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.liga.net',
        'url_prefix': 'https://www.liga.net',
        'url_template': 'https://www.liga.net/archive/{date}/all/page/{page_number}',
        'selectors': {
            'main_container': 'div.archive-materials>div.news-col',
            'title': 'div.news-col.clearfix>ul>li>a::text',
            'text': 'div#news-text',
            'link': 'div.news-col.clearfix>ul>li>a::attr(href)',
            'date': 'div.news-col.clearfix>ul>li>div.time::text',
            'category': 'span.news-nth-title-category::text',
            'subtitle_in_text': 'p.descr::text',
            'next_page': 'div.pages > a[title="Next page"]::attr(href)'
        }
    },
    'unian': {
        'start_request_type': 'media_scraper',
        'domain': 'https://www.unian.ua',
        'url_prefix': '',
        'url_template': 'https://www.unian.ua/news/archive/{date}',
        'selectors': {
            'main_container': 'div.col-md-8.pl0.col-sm-12.sm-prl0>div.list-thumbs__item>div.list-thumbs__info',
            'title': 'a.list-thumbs__title::text',
            'subtitle_in_text': 'p.article__like-h2::text',
            'text': 'div.article-text',
            'link': 'a.list-thumbs__title::attr(href)',
            'date': 'div.list-thumbs__time.time::text',
            'category_in_text': 'a.article__info-item.gray-marker::text',
            'views_in_text': 'span.article__info-item.views::text'
        }
    },
    'LB': {
        'start_request_type': 'media_scraper',
        'domain': 'https://ukr.lb.ua',
        'url_prefix': '',
        'url_template': 'https://lb.ua/archive/{date}',
        'selectors': {
            'main_container': 'ul.lenta > li.item-news',
            'title': 'a::text',
            'text': 'article.material',
            'subtitle': '::text',
            'link': 'div.title > a::attr(href)',
            'date': 'time::attr(datetime)',
            'category_in_text': 'div.date a::text'
        }
    },
    # zik requires AUTOTHROTTLE_ENABLED = true and futher delays
    'zik': {
        'start_request_type': 'media_scraper',
        'domain': 'zik.ua',
        'url_prefix': 'https://zikua.tv',
        'url_template': 'https://zikua.tv/sitemap/{date}?pg={page_number}',
        'selectors': {
            'main_container': 'div.b-archive-news-list > ul.news-list > li.news-list-item',
            'title': 'a::text',
            'text': 'article.article',
            'link': 'a::attr(href)',
            'time': 'time.time::text',
            'next_page': 'div.b-archive-news-list > ul.pagination-box > li.active + li > a::attr(href)',
            'category_in_text': 'div.date-block a:nth-child(2)::text',
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
            'text': 'div.article__body,div.col-lg-8.col-md-12',
            'link': '::attr(href)',
            'date_in_text': 'p.time::text,div.article-content__date>i.timestamp-date::text',
            'category_in_text': 'div.breadcrumbs>ol>li>a::text',
            'subtitle_in_text': 'div.article__header_description>p::text,div.content-subtitle>h2::text'
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
            'text': 'div.article_text',
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
            'main_container': 'article.c-card.c-card--title-md.c-card--log',
            'title': 'h3.c-card__title > a::text',
            'text': 'div.c-card__box.c-card__body,div.e-content.c-video-text',
            'link': 'h3.c-card__title > a::attr(href)',
            'subtitle': 'div.c-card__lead > p::text',
            'date': 'footer.c-card__foot > time::attr(datetime)',
            'views': 'dd.i-reset--b.i-view::text',
            'category': 'footer.c-card__foot>a::text',
            # 'next_page': 'div.text-center > div.js-more::attr(data-source)',
        }
    },
    'gordonua': {
        'start_request_type': 'media_scraper',
        'domain': 'gordonua.com',
        'url_prefix': 'https://gordonua.com',
        'url_template': 'https://gordonua.com/ukr/news/archive/{date}.html',
        'selectors': {
            'main_container': 'div.row> div.span-8 > div.block > div.lenta > div.media > div.row > div.span-8',
            'title': 'div.lenta_head > a::text',
            'text': 'div.block.article',
            'subtitle': 'div.span-8 > div.a_description::text',
            'link': 'div.span-8 > div.lenta_head > a::attr(href)',
            'date': 'div.span-8 > div.for_data::text',
            'category': 'div.lenta_div>a::text'
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
            # 'text': 'div.content',
            'text': 'div[itemprop="articleBody"]',
            'subtitle': 'a > div.title_short::text',
            'link': 'a::attr(href)',
            'time': 'div.ni__date.lorange::text',
            'category_in_text':'div.nav>ul.nav-list>li.is-active>a::text'

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
            'category_in_text': 'span[itemprop="articleSection"]>a::text',
            'views_in_text': 'span.view::text',
            'next_page': 'div.b-page-selector-holder > ul >li.page_nav.next_page:not([class~=ina]) > a::attr(href)'
        }
    },
    'focus': {
        'start_request_type': 'pages_scraper',
        'domain': 'focus.ua',
        'url_prefix': 'https://focus.ua',
        'url_template': 'https://focus.ua/news?page={page_number}',
        'selectors': {
            'main_container': 'article.c-card-list.c-card-list--img',
            'title': 'a.c-card-list__link::text',
            'text': 'div.s-content',
            'link': 'a.c-card-list__link::attr(href)',
            'subtitle': 'div.c-card-list__description>p::text',
            'date': 'time.c-card-list__date::attr(datetime)',
            'category': 'a.c-card-list__category::text',
            'next_page': 'next_number'
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
            'text': 'div.article_content[itemprop="articleBody"]',
            'link': '::attr(href)',
            'date': 'div.text > div.tape_news__info > span.tape_news__date::text',
            'views': 'div.text > div.tape_news__info > span.tape_news__date::text',
            'next_page': 'ul.pagination > li.arrow:last-child > a::attr(href)',
            'category': 'div.tape_news__info>span.tape_news__tag::text'
        },
    },
    # у Свободы пока что умеем обрабатывать только 100 страниц
    # тому треба запускати по пів місяця, бо не всі дати влазять у 100 сторінок
    'svoboda': {
        'start_request_type': 'pages_scraper',
        'domain': 'www.radiosvoboda.org',
        'url_prefix': 'https://www.radiosvoboda.org',
        'url_template': 'https://www.radiosvoboda.org/z/630/{date_end}?p={page_number}',
        'selectors': {
            'main_container': '.content-offset .row>ul>li',
            'title': 'div.media-block > a::attr(title)',
            # 'text': 'div.body-container,div.intro.m-t-md',
            'text': 'div#article-content>div.wsw,div.intro.m-t-md',
            'link': 'div.media-block > a::attr(href)',
            'date': 'div.media-block span.date ::text',
            'category_in_text': 'div.category>a::text',
            'date_in_text': 'span.date>time::attr(datetime)',
            # 'next_page': 'p.buttons.btn--load-more > a::attr(href)',
            'next_page': 'next_number'
        }
    },
    '112': {
        #robots_obey = False in settings
        'start_request_type': 'media_scraper',
        'domain': '112.ua',
        'url_prefix': 'https://ua.112ua.tv',
        'url_template': 'https://ua.112ua.tv/archive?date_from={date}&date_to={date}&guest_and_news=&category=&type=',
        'selectors': {
            'main_container': 'div.decs-list',
            'title': 'a::text',
            # 'text': 'article.article-content.page-cont',
            'text': 'div.article-content_text',
            'link': 'a::attr(href)',
            'date': 'div > span::text',
            'time': 'div > span > time::text',
            'category_in_text': 'ul.row.align-middle li.breadcrumbs-link:last-child span::text',
            'subtitle_in_text': 'p.top-text::text',
            'next_page': 'ul.pagination > li.next> a::attr(href)'
        }
    },
    'dzerkalo_tyzhnya': {
        'start_request_type': 'media_scraper',
        'domain': 'https://dt.ua/',
        'url_prefix': 'https://zn.ua',
        'url_template': 'https://zn.ua/ukr/all-news/date={date}',
        'selectors': {
            'main_container': 'div.news_list.news_block > div.news_block_item',
            'title': 'a.news_item.sunsite_action::text',
            'subtitle': 'span.news_summary::text',
            'link': 'a::attr(href)',
            'text': 'div.bottom_block div.article_body',
            'time': 'div.news_block_item::attr(data-type)',
            'next_page': 'div.navigate > span.next>a::attr(href)',
            'category_in_text': 'ol.breadcrumb_main li[itemprop="itemListElement"]:last-child span::text',
            'next_page_number': 'page_and_date'
        }
    },
    'strana': {
        'start_request_type': 'media_scraper',
        'domain': 'strana.ua',
        'url_prefix': 'https://strana.ua',
        'url_template': 'https://strana.ua/news/day={date}/page-{page_number}.html',
        'selectors': {
            'main_container': 'article.lenta-news.clearfix',
            'title': 'div > div.title > a::text',
            'text': 'div#article-body',
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
            'text': 'div.article-body',
            'subtitle': 'div.b-card--caption > h5::text',
            'link': '::attr(href)',
            'date': 'div.b-card--caption > time::text',
            # 'category_in_text': 'span.label.label-category::text',
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
            'text': 'div.kv-post-content-text',
            'link': 'a::attr(href)',
            'subtitle': 'a>div.category_tape_exerpt>p::text',
            'date': 'i.time::text',
            'next_page': 'nav.prev-next-posts>div.prev-posts-link>a::attr(href)',
            'category_in_text': 'div.fakty_breadcrumbs > span:last-child span::text'
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
            'next_page': 'div.pager > a:last-child::attr(href)',
            'category_in_text': 'h3.category-title>a::text',
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
    # sraped correctly only when in 10-days intervals
    'hromadske': {
        'start_request_type': 'pages_scraper',
        'domain': 'https://hromadske.ua/',
        'url_prefix': 'https://hromadske.ua',
        'url_template': 'https://hromadske.ua/news?page={page_number}',
        'selectors': {
            'main_container': '.NewsPostList > .NewsPublicationCard',
            'title': 'div.NewsPublicationCard-title::text',
            'link': '::attr(href)',
            'text': 'div.PostContent-body',
            # 'time': 'div.NewsPublicationCard-time::text',
            'next_page': 'div.NewsPostList-loadMore> a::attr(href)',
            'next_page_number': 'only_page_number',
            'date_header': 'div.NewsPostList > div.DateHeader > span::text',
            'category_in_text': 'a.PostHeader-topic>div::text',
            'date_in_text': 'div[itemprop="datePublished"]::attr(content)'
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
            # 'time': 'div.time::text',
            'text': 'div.article',
            'next_page': 'div.b_center_pager>ul.pager_list li.page+li.arrow>a::attr(href)',
            'next_page_number': 'only_page_number',
            'date_header': 'div.news-list.big.time-stamp > h2::text',
            'category_in_text': 'div.breadcrumbs a:nth-child(3)::text',
            'date_in_text': 'div.authorDate>span[itemprop="datePublished"]::text'
        }
    },
    # цензор банить, якщо великий інтервал дат. збільшення time_out in setting doesn`t help
    'censor': {
        'start_request_type': 'media_scraper',
        'domain': 'https://censor.net.ua',
        'url_prefix': '',
        # 'url_template': 'https://censor.net.ua/news/all/page/{page_number}/category/0/interval/5/sortby/date',
        'url_template': 'https://censor.net/news/all/page/{page_number}/archive/{date}/category/0/sortby/date',
        'selectors': {
            'main_container': 'section.news article.item',
            'title': 'h3>a::text',
            'subtitle': 'div.anounce > a::text',
            'link': 'div.anounce > a::attr(href)',
            'text': 'div.text',
            # 'text': 'section.hnews.hentry.item',
            # 'text': 'div.entry-content._ga1_on_[itemprop="articleBody"]',
            'date': 'time::attr(datetime)',
            'views': 'div.hit > span > span.info::text',
            # 'next_page': 'div.news_paging:nth-child(1)  a.pag_next::attr(href)',
            'next_page': 'table.pag_table a.pag_next::attr(href)',
            'category_in_text': 'span.span_h2>a.category::text'
        }
    },
    'korrespondent': {
        'start_request_type': 'media_scraper',
        'domain': 'https://ua.korrespondent.net/',
        'url_prefix': '',
        'url_template': 'https://ua.korrespondent.net/all/{date}/p{page_number}/',
        'selectors': {
            'main_container': 'div.articles-list div.article',
            'title': 'h3 > a::text',
            'subtitle': 'div.article__text::text',
            'link': 'h3 > a::attr(href)',
            'text': 'div.post-item__text',
            'date': 'div.article__date::text',
            'category': 'a.article__rubric::text',
            'views_in_text': 'div.post-item__views span::text',
            'next_page': 'li.pagination__item_last.pagination__item > a.pagination__link.pagination__forward::attr(href)'
        }
    },
    'glavcom': {
        'start_request_type': 'media_scraper',
        'domain': 'glavcom.ua',
        'url_prefix': 'https://glavcom.ua',
        'url_template': 'https://glavcom.ua/news/archive/{date}.html',
        'selectors': {
            'main_container': 'div.block.news_list > ul > li',
            'title': 'time + a::text',
            'subtitle': 'div.header::text',
            'text': 'div.body',
            'link': 'time + a::attr(href)',
            'category_in_text': 'div.col-xs-12.col-md-8>div.chapter>a::text',
            'date': 'time::text'
        }
    },
    'vgolos': {
        'start_request_type': 'media_scraper',
        'domain': 'vgolos.com.ua',
        'url_prefix': 'https://vgolos.com.ua',
        'url_template': 'https://vgolos.com.ua/archive/{date}?offset={page_number}',
        'selectors': {
            'main_container': 'article',
            'title': 'h4 > a::text',
            'text': 'main#page-content',
            'link': 'h4 > a::attr(href)',
            'date': 'div.data>time::text',
            'date_in_text': 'h1+time::text',
            'next_page': 'next_number'
        }
    },
    'nv': {
        'start_request_type': 'media_scraper',
        'domain': 'nv.ua',
        'url_template': 'https://nv.ua/sitemap_{date}.html',
        'selectors': {
            'main_container': 'div.row > div.col-xs-12 ~ p',
            'title': 'a::text',
            'text': 'div.article__content__body',
            'link': 'a::attr(href)', 
            'date_in_text': 'div.article__head__additional_published::text', 
            'category_in_text': 'li.sub_category.active>a::text'
        }
    },
    'gazetaua': {
        'start_request_type': 'media_scraper',
        'domain': 'gazeta.ua',
        'url_prefix': 'https://gazeta.ua',
        'url_template': 'https://api.gazeta.ua/api/section/stream?page={page_number}&date={date}&category=&specs=stream&lang=uk&template=slim&limit=20',
        'selectors': {
            'main_container': 'div.news-wrapper div.content.ml160',
            'title': 'a.news-title.block.black.fs16.mb5::text',
            'time': 'section.span-info span.red:first-child::text',
            'date': 'section.span-info span:nth-child(2)::text',
            'views': 'section.span-info span:nth-child(4)::text',
            'text': 'article',
            'link': 'a.news-title.block.black.fs16.mb5::attr(href)', 
            'category_in_text': 'div.pull-right.news-date+div>a.w-title::text',
            'next_page': 'next_number'
        }
    },
    'ukrinform': {
        'start_request_type': 'pages_scraper',
        'domain': 'ukrinform.ua',
        'url_prefix': 'https://www.ukrinform.ua',
        'url_template': 'https://www.ukrinform.ua/block-lastnews?page={page_number}',
        'selectors': {
            'main_container': 'section.restList article',
            'title': 'h2 > a::text',
            'text': 'div.newsText',
            'subtitle': 'section p::text',
            'link': 'h2 > a::attr(href)',
            'date': 'section > time::attr(datetime)',
            'category_in_text': 'ul.leftMenu li>a>span::text',
            'next_page': 'next_number'
        }
    },
    'suspilne': {
        'start_request_type': 'media_scraper',
        'domain': 'suspilne.media',
        'url_template': 'https://suspilne.media/archive/{date}/',
        'selectors': {
            'main_container': 'a.c-article-card',
            'title': 'span.c-article-card__headline-inner::text',
            'date': 'div.c-article-card__info > time.c-article-card__info__time::text',
            'text': 'div.c-article-content.c-article-content--bordered',
            'link': 'a::attr(href)', 
            'category_in_text': 'div.c-article-label a.c-article-label__item::text'
        }
    },
    'babel': {
        'start_request_type': 'media_scraper',
        'domain': 'babel.ua',
        'url_template': 'https://babel.ua/text-sitemap/{date}',
        'selectors': {
            'main_container': 'div:nth-child(7) > ul > li',
            'title': 'a::text',
            'text': 'div.c-post-text.js-article-content',
            'link': 'a::attr(href)',
            'date_in_text': 'div.c-post-data-box time::attr(datetime)'
        }
    },
    'zaxid': {
        'start_request_type': 'pages_scraper',
        'domain': 'zaxid.net',
        'url_template': 'https://zaxid.net/news/',
        'selectors': {
            'main_container': 'div.row div.news-list.archive-list  ul.list > li',
            'title': 'a > div.news-title::text,div.title::text',
            'text': 'div.article_news.next-article div#newsSummary',
            'link': 'a::attr(href)',
            'time': 'a > div.time::text',
            'category_in_text': 'div.info_wrap>a.category::text',
            'date_header': 'div.row div.news-list.archive-list  h5.center_title > span::text',
            'next_page': 'div.b_center_pager li.arrow:last-child > a::attr(href)'
        }
    },
    'telegraf': {
        'start_request_type': 'media_scraper',
        'domain': 'telegraf.com.ua',
        'url_template': 'https://telegraf.com.ua/date/{date}/page/{page_number}/',
        'selectors': {
            'main_container': 'div.Nitem div.right',
            'title': 'a::text',
            'subtitle': 'p::text',
            'text': 'div.content-single__block_text_body',
            'link': 'a::attr(href)',
            'time': 'div.time::text',
            'category_in_text': 'div.pull-left>ul>li.active>a::text',
            'views_in_text': 'div.article-announcement-view>b::text',
            'next_page': 'a.next.page-numbers::attr(href)'
        }
    },
    'kp': {
        'start_request_type': 'media_scraper',
        'domain': 'kp.ua',
        'url_template': 'https://kp.ua/archive/{date}/',
        'selectors': {
            'main_container': 'ul.news-online.news-per-day li',
            'title': 'a::attr(title)',
            'text': 'div.content',
            'link': 'a::attr(href)',
            'time': 'a>span::text',
            'subtitle_in_text': 'div.content-info::text',
            'category_in_text': 'div.breadcrumbs>span[typeof="v:Breadcrumb"]>a::text'
        }
    },
    'fakty': {
        'start_request_type': 'media_scraper',
        'domain': 'fakty.ua',
        'url_prefix': 'https://fakty.ua',
        'url_template': 'https://fakty.ua/archive/{date}',
        'selectors': {
            'main_container': 'div.items div.my-flex-block1',
            'title': 'a.tit>p::text',
            'text': 'div#article_content3',
            'link': 'a.tit::attr(href)',
            'time': 'span.mytime::text',
            'date': 'span.mydate::text',
            'views': 'span.stat_text::text',
            'category_in_text': 'span.fl_l.my_rubrika>a::text',
            'next_page': 'div.pager>ul li.page.active+li>a::attr(href)'
        }
    }
}
