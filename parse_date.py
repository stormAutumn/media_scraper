import dateparser
# from m_pages_config import media_with_pages_config


def parse_date(media, date_response_format):
    if media == 'unian':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%H:%M , %d.%B.%Y'], languages=['uk'])
    if media == 'znaj':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%H:%M %d.%m'], languages=['uk'])
    if media == '24tv':
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
    if media == 'strana' or media == 'ukranews':
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
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%Y-%m-%dT%H:%M:%S+03:00'], languages=['uk'])
    if media == 'liga':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d.%m.%Y %H:%M'], languages=['uk'])
    if media == 'espreso':
        date_parsed = dateparser.parse(date_response_format, date_formats=[
            '%d %B, %Y'], languages=['uk'])

    return date_parsed
