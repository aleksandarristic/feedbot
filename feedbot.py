from __future__ import annotations

import re
import json
from datetime import datetime

import requests
import rfeed
from bs4 import BeautifulSoup


def convert_date(date: str, feed_source: dict) -> datetime | None:
    link_re = feed_source['date_re']
    link_months = feed_source.get('months')

    match = re.search(link_re, date)
    if not match:
        return None
    year = int(match.groupdict()['y'])
    if link_months:
        month = link_months.index(match.groupdict()['m']) + 1
    else:
        month = int(match.groupdict()['m'])

    day = int(match.groupdict()['d'])
    return datetime(year=year, day=day, month=month)


def build_feed(feed_source: dict) -> str:
    r = requests.get(feed_source['link'])
    html_page = r.text
    parser = BeautifulSoup(html_page, 'html.parser')

    news_items = parser.find_all(**feed_source['locators']['item'])

    feed = rfeed.Feed(
        title=feed_source['name'],
        link=feed_source['link'],
        description=feed_source['name'],
        language=feed_source.get('lang')
    )

    for news_item in news_items:
        date = news_item.find(**feed_source['locators']['date']).text
        description = news_item.find(**feed_source['locators']['description']).text
        link = feed_source['base'] + news_item.find(**feed_source['locators']['link']).attrs['href']
        title = news_item.find(**feed_source['locators']['title']).text

        if len(title) > 30:
            title = title[:27] + '...'

        author = feed_source['author']
        feed.items.append(rfeed.Item(
            title=title,
            link=link,
            description=description,
            author=author,
            guid=rfeed.Guid(link),
            pubDate=convert_date(date, feed_source)
        ))

    rss = feed.rss()

    return rss


if __name__ == '__main__':
    print('Reading config from sources.json...')
    with open('sources.json', 'r') as f:
        SOURCES = json.load(f)
    print('Done.')

    for source_identifier, source_config in SOURCES.items():
        print(f'Building feed for {source_identifier}...')
        with open(f'{source_identifier}.xml', 'w') as f:
            f.write(build_feed(source_config))
        print(f'{source_identifier}.xml written.')
