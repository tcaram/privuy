import re
import socket
import ipwhois
import tldextract

from urllib.parse import urlparse, parse_qsl, unquote_plus, urljoin

def is_url1_relative_to_url2(url1, url2):
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc

    return domain1 == domain2


def get_url_parts(url):
    """ adapted from https://stackoverflow.com/a/9468284 """
    parts = urlparse(url)
    _query = frozenset(parse_qsl(parts.query))
    _path = unquote_plus(parts.path).rstrip("/")
    parts = parts._replace(query=_query, path=_path)

    return parts


def does_url1_eq_url2(url1, url2):
    return get_url_parts(url1) == get_url_parts(url2)


def shorten_selenium_exception_message(message):
    parts = message.split("\n")
    if len(parts) > 0:  # if the message is multi-line
        return parts[0]  # take the first line
    else:
        return message[:100]  # take the first 100 characteres


# def make_url_absolute(base, path):
#     # if path is already an absolute URL, it won't append the base URL
#     return urljoin(base, path)


def get_hostname(url):
    new_url = urlparse(url)
    return new_url.hostname


def does_host1_eq_host2(host1, host2):
    parts1 = tldextract.extract(host1)
    parts2 = tldextract.extract(host2)
    return parts1.suffix == parts2.suffix and parts1.domain == parts2.domain


# def fqdn_to_http_url(fqdn):
#     return make_url_absolute("http://", fqdn).replace("///", "//")


# def remove_port_from_url(url):
#     # https://www.rfc-editor.org/rfc/rfc3986#appendix-B
#     url_parsing = re.match(
#         r"^(([^:\/?#]+):)?(\/\/([^\/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?", url)

#     if url_parsing.group(5):  # url has port
#         url = url.replace(":" + url_parsing.group(5), "")

#     return url

def whois_host(url):
    hostname = get_hostname(url)

    try:
        ip = socket.gethostbyname(hostname)
    except Exception as err:
        print("Couldn't check IP", err)
        return (None, None)
    else:
        whois = ipwhois.IPWhois(ip)

        # retry until success...
        while True:
            try:
                res = whois.lookup_whois()
            except ipwhois.exceptions.WhoisRateLimitError:  # rate limited, sleep for 10 seconds
                print("rate limited, sleeping")
                time.sleep(10)
            except Exception as err:  # other error, retry
                print(err)
                continue
            except KeyboardInterrupt:
                break
            else:  # success, no exception
                break

        ip_country = res['nets'][0]['country']
        ip_provider = res['nets'][0]['description']

        return (ip, ip_country, ip_provider)

def clean_badger_data(data):
    return {
        "cookieblocked": data['cookieblocked'],
        "origins": data['origins'],
        "trackerCount": data['trackerCount']
    }
