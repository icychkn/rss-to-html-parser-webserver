#!/usr/bin/python3

from socketserver import TCPServer
from urllib.parse import unquote
import feedparser
import json
import http.server
import os.path
import requests

PORT = 8080
# change this to True to enable debugging or False to disable
debugging_enabled = False

TCPServer.allow_reuse_address = True


def debug(message):
    if debugging_enabled:
        print("DEBUG: " + message)



class RSSFeed:
    def reset_variables( self ):
        self.values = {
            'style'   : '',
            'contents': ''
            }
        # {contents} is all the rss entries, while {style} determines the look
        # of the whole feed
        self.base_html = '''
<html>
<head>
<style>
{style}
</style>
</head>
<body>
<div>{contents}</div>
</body>
</html>
'''


    def set_style( self, style ):
        self.values['style'] = style


    def add_entry( self, entry ):
        self.values['contents'] = self.values['contents'] + entry


    # formats base html content with the values previously set
    def get_html_content( self ):
        return self.base_html.format(**self.values)





# this class will create an html form of an rss entry, without dealing with any
# of the rss directly.
class RSSEntry():
    def reset_variables( self ):
        self.values = {
            'style': '',
            'title': 'placeholder title',
            'title_link': '',
            'title_style': '',
            'author': 'placeholder_author',
            'author_link': '',
            'author_style': '',
            'date': 'placeholder date',
            'date_style': '',
            'contents': 'placeholder contents',
            'contents_style': ''
        }
        # the base html content to be formatted before returning complete entry
        # the class attributes are meant to make it easy to set styles of the
        # elements using the style attribute in the RSSFeed
        self.base_html = '''
<div class="rss_entry">
<hr class="rss_entry_hr">
<a href={title_link} target="_blank" class="rss_entry_title"><h3>{title}</h3></a>
<a href={author_link} target="_blank" class="rss_entry_author"><b>{author}</b></a>
<br><div {date_style} class="rss_entry_date">{date}</div>
<div {contents_style} class="rss_entry_contents">{contents}</div>
<hr class="rss_entry_hr">
</div>
'''


    def set_title( self, title ):
        self.values['title'] = title


    def set_title_link( self, title_link ):
        self.values['title_link'] = title_link


    def set_author( self, author ):
        self.values['author'] = author


    def set_author_link( self, author_link ):
        self.values['author_link'] = author_link


    def set_date( self, published_parsed ):
        parsed_date = str(published_parsed.tm_year) + "-" + str(published_parsed.tm_mon) + "-" + str(published_parsed.tm_mday) + " " + str(published_parsed.tm_hour) + ":"
        if len(str(published_parsed.tm_min)) == 1:
          self.values['date'] = parsed_date + "0" + str(published_parsed.tm_min)
        else:
          self.values['date'] = parsed_date + str(published_parsed.tm_min)


    def set_contents( self, contents ):
        self.values['contents'] = contents


    def parse_entry( self, entry ):
        if 'title' in entry:
            self.set_title(entry['title'])
        if 'link' in entry:
            self.set_title_link(entry['link'])
        if 'author_detail' in entry:
            if 'name' in entry['author_detail']:
                self.set_author(entry['author_detail']['name'])
            if 'href' in entry['author_detail']:
                self.set_author_link(entry['author_detail']['href'])
        if 'published_parsed' in entry:
            self.set_date(entry['published_parsed'])
        if 'summary' in entry:
            self.set_contents(entry['summary'])


    # formats html content of entry with values[]
    def get_html_content( self ):
        return self.base_html.format(**self.values)



##########################################################
# the rss feed returned will be returned in this format: #
##########################################################
# -------------------------------------------------
# <a href={content_link}><h3>{title}</h3></a>
# <a href={author_link}><b>{author_name}</b></a>
# {date} <- "yyyy-mm-dd hh:mm"
# <div>{content}</div>
# -------------------------------------------------
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    rss_feed = RSSFeed()
    rss_entry = RSSEntry()
    # easily resets object's variables
    def reset_variables( self ):
        self.rss_feed.reset_variables()
        self.rss_entry.reset_variables()


    # the only error prevention this has is it checks to see if the parameter
    # 'feed' is in the sanitized_path
    def parse_link( self ): # -> string
        # ensure following variables are reset each time this function is called
        rss_link = ""
        rss_style = ""
        parsed_parameters = { }

        # parse path into a dictionary
        # ?parameter=value -> { "parameter": "value"}
        for pair in self.sanitized_path.split("?")[1].split("&"):
            key, value = pair.split("=")
            parsed_parameters[key] = value

        # if parameter(s) exists, return it
        if "feed" in parsed_parameters:
            rss_link = parsed_parameters["feed"]
        if "style" in parsed_parameters:
            rss_style = unquote(parsed_parameters["style"])
        return rss_link, rss_style


    # gets an rss feed from a url 'rss_feed' and converts it to html
    def rss_to_html( self, rss_url, style ):
        tree = feedparser.parse(rss_url)
        self.rss_feed.set_style(style)
        for entry in tree.entries:
            self.rss_entry.parse_entry(entry)
            self.rss_feed.add_entry(self.rss_entry.get_html_content())

        # return an html version of the rss feed
        return self.rss_feed.get_html_content()


    def send_page( self, page ):
        self.send_response(200)
        self.send_header("Content-Type", 'text/html')
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page.encode('utf-8'))


    def do_GET( self ):
        self.sanitized_path = self.path.lstrip("/.").replace("../", "")
        debug(self.path + " -> " + self.sanitized_path)
        self.reset_variables()
        html_content = ""

        rss_link, rss_style = self.parse_link()
        if rss_link != "":
            html_content = self.rss_to_html(rss_link, rss_style)
        else:
            response(404)
            print("ERROR: Unable to get rss link from path " + self.path)

        self.send_page(html_content)



with TCPServer(( "", PORT ), RequestHandler ) as httpd:
    print("serving at port ", PORT)
    httpd.serve_forever()
