from datetime import datetime
from datetime import timedelta
from media_config import media_config


def get_date(date, media):
    '''Returns date in format specific for each media'''
    if media == 'pravda' or media == 'epravda':
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        return day + month + year
    if media == 'svoboda' or media == 'LB':
        day = date.strftime("%#d")
        month = date.strftime("%#m")
        year = date.strftime("%Y")
        return year + '/' + month + '/' + day
    if media == 'obozrevatel':
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        return day + '-' + month + '-' + year
    if media == 'rbc' or media == 'tsn' or media == 'unn' or media == 'focus':
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        return year + '/' + month + '/' + day
    if media == '112' or media == 'liga' or media == 'zik'or media == 'dzerkalo_tyzhnya' or media == 'apostrophe':
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        return year + '-' + month + '-' + day
    if media == 'unian':
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        return year + month + day
    if media == 'strana':
        day = date.strftime("%#d")
        month = date.strftime("%#m")
        year = date.strftime("%Y")
        return year + '-' + month + '-' + day
    if media == 'segodnya':
        day = date.strftime("%#d")
        month = date.strftime("%#m")
        year = date.strftime("%Y")
        return year + '-' + month + '/' + year + '-' + month + '-' + day
    if media == '24tv':
        day = date.strftime("%#d")
        month = date.strftime("%B").lower()
        year = date.strftime("%Y")
        return day + '_' + month + '_' + year
    if media == 'gordonua':
        day = date.strftime("%#d")
        month = date.strftime("%#m")
        year = date.strftime("%Y")
        return day + '-' + month + '-' + year
    if media == 'ukranews' or media == 'interfax':
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        return day + '.' + month + '.' + year
    if media == 'politeka':
        day = date.strftime("%d")
        month = date.strftime("%m")
        return day + '.' + month


def get_media_url(media, date=None, date_end=None, page_number=None):
    '''Returns url ready for scraper applying date to url template of provided media'''
    media_url_template = media_config.get(media).get('url_template')
    date_formatted = get_date(date, media)
    date_end_formatted = None
    if date_end != None:
        date_end_formatted = get_date(date_end, media)

    return media_url_template.format(
        date=date_formatted,
        date_end=date_end_formatted,
        page_number=page_number,
    )


def get_media_urls_for_period(media, date_start=None, date_end=None, page_number=None):
    '''Returns array of dates for media for period'''
    urls = []
    current_dates = []
    current_date = date_start
    if date_end != None:
        while current_date <= date_end:
            url = get_media_url(media, current_date, date_end, page_number)
            urls.append(url)
            current_dates.append(current_date)
            current_date += timedelta(days=1)
    else:
        url = get_media_url(media, current_date, page_number)
        urls.append(url)
        current_dates.append(current_date)
    return urls, current_dates


print(
    get_media_urls_for_period(
        'hromadske_radio',
        page_number=1
    )
)

# print(
#     get_media_url(
#         'hromadske_radio',
#         date=datetime(2020, 4, 1),
#         page_number=1
#     )
# )
