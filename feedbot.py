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
    try:
        year = int(match.groupdict()['y'])
        if link_months:
            m_str = match.groupdict()['m']
            if m_str not in link_months:
                return None
            month = link_months.index(m_str) + 1
        else:
            month = int(match.groupdict()['m'])
        day = int(match.groupdict()['d'])
        return datetime(year=year, day=day, month=month)
    except (ValueError, KeyError):
        return None


def build_feed(feed_source: dict) -> str:
    try:
        r = requests.get(feed_source['link'], timeout=30)
        r.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"  Timeout fetching {feed_source['link']}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"  Network error fetching {feed_source['link']}: {e}")
        raise

    parser = BeautifulSoup(r.text, 'html.parser')
    news_items = parser.find_all(**feed_source['locators']['item'])

    feed = rfeed.Feed(
        title=feed_source['name'],
        link=feed_source['link'],
        description=feed_source['name'],
        language=feed_source.get('lang')
    )

    for news_item in news_items:
        try:
            date_el = news_item.find(**feed_source['locators']['date'])
            desc_el = news_item.find(**feed_source['locators']['description'])
            link_el = news_item.find(**feed_source['locators']['link'])
            title_el = news_item.find(**feed_source['locators']['title'])

            if not all([date_el, desc_el, link_el, title_el]):
                print(f"  Skipping item: missing one or more required elements")
                continue

            date = date_el.text
            description = desc_el.text
            link = feed_source['base'] + link_el.attrs['href']
            title = title_el.text
        except (AttributeError, KeyError) as e:
            print(f"  Skipping item due to parse error: {e}")
            continue

        author = feed_source['author']
        feed.items.append(rfeed.Item(
            title=title,
            link=link,
            description=description,
            author=author,
            guid=rfeed.Guid(link),
            pubDate=convert_date(date, feed_source)
        ))

    return feed.rss()


if __name__ == '__main__':
    print('Reading config from sources.json...')
    with open('sources.json', 'r') as f:
        SOURCES = json.load(f)
    print('Done.')

    for source_identifier, source_config in SOURCES.items():
        print(f'Building feed for {source_identifier}...')
        try:
            rss = build_feed(source_config)
            with open(f'{source_identifier}.xml', 'w') as f:
                f.write(rss)
            print(f'{source_identifier}.xml written.')
        except Exception as e:
            print(f'  Failed to build feed for {source_identifier}: {e}')
