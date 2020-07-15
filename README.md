# rss-to-html-parser-webserver
A simple custom webserver written in Python, with the sole purpose of getting an rss feed from GET requests, converting the feed into an html form that can then
be displayed in an iframe.

This project is intended to be a self-hostable alternative to online rss-to-html generators. Extremely simple to host, just change port to listen on, and let it
run. Feel free to modify it to the way you want it to be.

## how does it work?
The server doesn't store any rss feeds, it works completely by parsing GET requests to get the information it needs to find the rss feed. The following html code
is the minimum required to embed an rss feed into a page:

<iframe type="text/html" src="http://{url/ip/domain name of server}/?feed={link to rss feed}" height="480" width="480"></iframe><br>

iframe sends get request to server<br>
server extracts rss feed from get request<br>
server downloads and parses the rss feed into a dict like variable<br>
server forms a summary from the feed in an html format<br>
server then returns html form as a response to the get request<br>
iframe displays html as embedded

I added a way to set css styles with this as well, using a "style" parameter and including it in the returned html. The css needs to be encoded into a url-friendly
form before it can be included in the url. I will also include a script that takes the name of a css file, opens it, and returns the contents encoded in a
url-friendly form. This can then be added directly to the url to get the resulting url:

<iframe type="text/html" src="http://{url/ip/domain name of server}/?feed={link to rss feed}&style={css url-friendly content}" height="480" width="480"></iframe><br>

Note: this script has very poor error handling. If it fails, it will crash and let you know.

## License
Don't know what license is the most permissible. Do whatever you want with this.
