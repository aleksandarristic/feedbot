# feedbot

A simple python web scraper and rss xml generator.

When I discovered that SRB CERT doesn't have an RSS feed that I could follow, I decided to build this little scraper. I use it on my own server to fetch and parse a page on Serbian CERT, and convert the fetched items to an RSS feed that I serve for my own purposes. Feel free to take a look at the ```sources.json```, I've included the SRB CERT configuration that should work out of the box.

### Instructions

##### Note: tested and working with Python 3.8.16 on Ubuntu 20.04.

##### Note #2: This python script only generates the RSS xml file; you need to serve it using your server (nginx in my case). 

1. Clone, setup virtualenv, install requirements
```commandline
git clone https://github.com/aleksandarristic/feedbot.git
cd feedbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Edit ```update_feeds.sh``` to adjust your paths
```commandline
vim update_feeds.sh
```

3. Set up crontab according to contents of ```cron``` file via
```commandline
sudo crontab -e
```

Test by running update_feeds.sh manually as sudo:
```commandline
sudo ./update_feeds.sh
```

If everything was configured correctly, you should see xml files generated in the path where you cloned the repo, and copied to your web server directory as set up in the ```update_feeds.sh```.


### Configuration

Set your configuration in the ```sources.json``` file like so:
```json
{
    "feed_id": {  // Your own unique identifier of this feed; used in print statements when generating an xml file

        "name": "Human readable name", // Used for rss feed title
        "lang": "en", // language code
        "author": "Author name", // All items will have this author
        "slug": "human_readable_name_blah_blah", // Should be filesystem-friendly since the end product is slug value with .xml extension
        "link": "https://my.blog/latest-entries.html", // Page to scrape for new entries 
        "base": "https://my.blog/posts/", // Base url for individual items; can be an empty string if your items have a full URL
        "date_re": "(?P<d>\\d+)\\. (?P<m>\\d+). (?P<y>\\d+).", // regex to capture date from text; hackity hack 
        "months": ["јан", "феб", "..."], // [optional] mapping of months; we want to avoid changing locales to read a 
                                         // long month names; instead, just read this list and match values to get the month
      
        "locators": {  // this section describes locators to use with BeautifulSoup4 html parser
          
            // item is the base item that is one news item, blog post or whatever you are parsing.
            // item html element should contain all other elements
            "item": {
                // this is the element that holds each individual entry all other locators are searching within the item
                "name": "div",
                "attrs": {
                    "class": "preporuka"
                }
            },
          
            // this is the item title
            "title": {    // item title is fetched from 'h3' element with class 'title'
                "name": "h3",
                "attrs": {
                    "class": "title"
                }
            },
          
            // this is the item description
            "description": {   // item description is fetched from 'h3' element with class 'title'
                "name": "h3",
                "attrs": {
                    "class": "title"
                }
            },
          
            // this is the date of item publishing; the contents of this element .text should be parsed via the regex from date_re
            "date": {         // date is fetched from 'span' element with class set to 'date'
                "name": "span",
                "attrs": {
                    "class": "date"
                }
            },
          
            // this is the link to the full item
            "link": {       // link is fetched from 'a' element with class 'date'.
                "name": "a",
                "attrs": {
                    "class": "date"
                }
            }
        }
    }

```
Note that ```link``` locator is special; this is the only element where we are fetching ```['href']``` instead of ```.text``` from the bs4 element. 

### TODOs

* Better generalization for fetching of individual item properties to cover edge cases.
* Parse dates in a more sane way (no moar haxx)/.
* Create more sample configurations
* Docs. Docs in code. Docs online.