import platform
import dateparser
from datetime import datetime
from datetime import timedelta
from media_config import media_config
import re


if platform.system() == 'Windows':
    no_zero_format = "%#"
else:
    no_zero_format = "%-"


def get_date(date, media):
    '''Returns date in format specific for each media'''
    if media == 'pravda' or media == 'epravda':
        day = date.strftime("%d")
        month = date.strftime("%m")
        year = date.strftime("%Y")
        return day + month + year
    if media == 'svoboda' or media == 'LB':
        day = date.strftime(no_zero_format + "d")
        month = date.strftime(no_zero_format + "m")
        year = date.strftime("%Y")
        return year + '/' + month + '/' + day
    if media == 'obozrevatel' or media=='glavcom':
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
        day = date.strftime(no_zero_format + "d")
        month = date.strftime(no_zero_format + "m")
        year = date.strftime("%Y")
        return year + '-' + month + '-' + day
    if media == 'segodnya':
        day = date.strftime(no_zero_format + "d")
        month = date.strftime(no_zero_format + "m")
        year = date.strftime("%Y")
        return year + '-' + month + '/' + year + '-' + month + '-' + day
    if media == '24tv':
        day = date.strftime(no_zero_format + "d")
        month = date.strftime("%B").lower()
        year = date.strftime("%Y")
        return day + '_' + month + '_' + year
    if media == 'gordonua':
        day = date.strftime(no_zero_format + "d")
        month = date.strftime(no_zero_format + "m")
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
    if media == 'korrespondent':
        year = date.strftime("%Y")
        month = date.strftime("%B").lower()
        return year + '/' + month



def get_media_url(media, date=None, date_end=None, page_number=None):
    '''Returns url ready for scraper applying date to url template of provided media'''
    media_url_template = media_config.get(media).get('url_template')
    date_formatted = None
    if date != None:
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
            # korrespondent shows news by month, so next date will be the first day of next month
            if media=='korrespondent':
                current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            else:
                current_date += timedelta(days=1)
    else:
        url = get_media_url(media, current_date, page_number)
        urls.append(url)
        current_dates.append(current_date)
    return urls, current_dates


def parse_date(media, date_response_format):
    if media == 'unian':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%H:%M , %d.%B.%Y'], languages=['uk'])
    if media == 'znaj':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%H:%M %d.%m'], languages=['uk'])
    if media == '24tv' or media=='glavcom':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B, %H:%M'], languages=['uk'])
    if media == 'gordonua':
        date_response_format = date_response_format.replace(
            ".", ":").replace("i", "і")
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B, %Y %H:%M'], languages=['uk'])
    if media == 'LB':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%Y-%m-%dT%H:%M:%SZ'], languages=['uk'])
    if media == 'ictv':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%B, %d о %H:%M'], languages=['uk'])
    if media == 'strana':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B %Y, %H:%M'], languages=['ru'])
    if media == 'ukranews':
        date_response_format = date_response_format.rsplit(' ', 1)[0]
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B %Y, %H:%M'], languages=['ru'])
    if media == 'znaj':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%H:%M, %d.%m'], languages=['uk'])
    if media == '112':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d.%m.%Y'], languages=['uk'])
    if media == 'svoboda':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B %Y'], languages=['uk'])
    if media == 'politeka':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%H:%M %d.%m'], languages=['uk'])
    if media == 'interfax' or media == 'hromadske_radio':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d.%m.%Y'], languages=['uk'])
    if media == 'censor' or media == 'tsn':
        # get rid of +02:00 or +03:00
        date_response_format = re.sub(r'\+0\d\:00', '', date_response_format)
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%Y-%m-%dT%H:%M:%S'], languages=['uk'])
    if media == 'liga':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d.%m.%Y %H:%M'], languages=['uk'])
    if media == 'espreso':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B, %Y'], languages=['uk'])

    if media == 'hromadske':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B'], languages=['uk'])

    if media == 'korrespondent':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B %Y, %H:%M'], languages=['uk'])

    return date_parsed


def get_clean_text(dirty_text_list):
    joined_text = ''.join(dirty_text_list)
    text_stripped = joined_text.strip()
    text_clean = text_stripped.replace('\n,', '').replace('\t', '')
    return text_clean


def get_clean_time(time_text):
    joined_text = ''.join(time_text)
    time = joined_text.replace(',', '').replace('\n', '')
    time_stripped = time.strip()
    time_parsed = datetime.strptime(
        time_stripped, "%H:%M").time()
    return time_parsed
