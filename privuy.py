import re
import json
import time
import random
import requests

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from selenium.webdriver.common.by import By
import selenium.common.exceptions

from storage import Store
from utils import is_url1_relative_to_url2, does_url1_eq_url2, shorten_selenium_exception_message, clean_badger_data, get_hostname, whois_host

class PrivUY:
    LOAD_TIME_WAIT = 5  # seconds
    MAX_CRAWLING_LINKS_PER_SITE = 3

    def __init__(self):
        self.options = Options()

        self.options.add_extension('privacy_badger-chrome.crx')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument("--disable-browser-side-navigation")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("start-maximized")
        self.options.add_argument("enable-automation")
        self.options.add_argument("--dns-prefetch-disable")
        self.options.add_argument('--log-level=3')

        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=self.options)

        self.driver.set_page_load_timeout(10)
        self.driver.set_script_timeout(10)
        self.driver.maximize_window()

        self.store = Store("reports.csv")

        with open("js/get_badger_data.js", "r", encoding="utf-8") as file:
            self.badger_script = file.read()
        
        with open("input/domain_list.txt", "r", encoding="utf-8") as file:
            self.fqdn_list = file.readlines()
            self.fqdn_list = [site.rstrip() for site in self.fqdn_list]
        
    def get_badger_data(self):
        """open new tab and load privacy badger's options"""

        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(
            "chrome-extension://pkehgijcmpdhfbdbbnkijodmdjhbjlgp/skin/options.html")

        # inject the script to fetch the report
        data = self.driver.execute_script(self.badger_script)

        # close tab and focus the main window
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        return data

    def close_init_badger_tab(self):
        """ wait for privacy badger to initialize and close the welcome tab when it opens """

        WebDriverWait(
            self.driver, 10).until(
            lambda x: len(
                self.driver.window_handles) == 2)

        # at this point we can ensure that the second opened tab is privacy
        # badger's, so we can safely close it
        window1 = self.driver.window_handles[1]
        self.driver.switch_to.window(window_name=window1)
        self.driver.close()

        # now we switch back to the main tab
        self.driver.switch_to.window(self.driver.window_handles[0])

    def get_site_and_scroll(self, site_url):
        """ navigate to a site and scroll down during LOAD_TIME_WAIT """

        self.driver.get(site_url)
        self.driver.implicitly_wait(self.LOAD_TIME_WAIT)

        self.raise_on_chrome_error_pages()
        self.scroll_page()

    def gather_privacy_report(self, site_url):
        privacy_report = {
            "badger": [],
            "ip": {
                "address": None,
                "country": None,
                "provider": None
            }
        }

        self.get_site_and_scroll(site_url)
        urls = [site_url] + self.gather_internal_links()

        for k, url in enumerate(urls):
            if k != 0:  # urls[0] = site_url, don't load it as it's already loaded
                self.get_site_and_scroll(url)

            if privacy_report["ip"]["address"] is None:
                address, country, provider = whois_host(url)
                privacy_report["ip"]["address"] = address
                privacy_report["ip"]["country"] = country
                privacy_report["ip"]["provider"] = provider

                # print(address, country, provider)

            privacy_report["badger"].append(clean_badger_data(
                self.get_badger_data()))  # always at the end

        return privacy_report

    def gather_internal_links(self):
        urls = []
        anchors = self.driver.find_elements(by=By.TAG_NAME, value="a")

        for anch in anchors:
            try:
                href = anch.get_attribute("href")
            except selenium.common.exceptions.StaleElementReferenceException:  # element is not in DOM anymore, skip
                continue

            if not isinstance(href, str):
                continue

            if not href.startswith("http"):  # url is not a website
                continue

            if not is_url1_relative_to_url2(
                    self.driver.current_url,
                    href):  # url is not within the same site
                continue

            if "#" in href:  # is a target link
                continue

            if does_url1_eq_url2(self.driver.current_url, href):
                # discard the url if it points to the same resource as the site, i.e:
                # gub.uy === gub.uy/ === www.gub.uy === https://gub.uy:80/ """
                continue

            urls.append(href)

            if len(urls) == self.MAX_CRAWLING_LINKS_PER_SITE:
                break

        return urls

    def raise_on_chrome_error_pages(self):
        """ adapted from https://github.com/EFForg/badger-sett/crawler.py """

        actual_page_url = self.driver.execute_script(
            "return document.location.href")
        if not actual_page_url.startswith("chrome-error://"):
            return

        error_text = self.driver.find_element(By.TAG_NAME, "body").text
        error_code = error_text

        # for example: ERR_NAME_NOT_RESOLVED
        matches = re.search('(ERR_.+)', error_text)
        if not matches:
            # for example: HTTP ERROR 404
            matches = re.search('(HTTP ERROR \\d+)', error_text)
        if matches:
            error_code = matches.group(1)

        if error_code:
            msg = "Reached error page: " + error_code
        else:
            msg = "Reached unknown error page (basic auth prompt?)"

        raise selenium.common.exceptions.WebDriverException(msg)

    def scroll_page(self):
        """ adapted from https://github.com/EFForg/badger-sett/crawler.py """

        # split self.LOAD_TIME_WAIT into INTERVAL_SEC intervals
        INTERVAL_SEC = 0.1

        def _scroll_down():
            self.driver.execute_script("window.scrollBy(0, arguments[0]);", abs(random.normalvariate(50, 25)))

        for _ in range(int(self.LOAD_TIME_WAIT / INTERVAL_SEC)):
            time.sleep(INTERVAL_SEC)
            # scroll a bit during every interval
            _scroll_down()

    def start(self):
        self.close_init_badger_tab()

        for k, fqdn in enumerate(self.fqdn_list):
            if self.store.exists(fqdn):
                continue

            print(k, fqdn)

            url = fqdn
            if "http://" not in url:
                url = "http://" + url

            report = {}
            try:
                report = self.gather_privacy_report(url)
            except selenium.common.exceptions.WebDriverException as err:
                print(fqdn, "skipping due to exception:", shorten_selenium_exception_message(str(err)))
                continue

            self.store.save(fqdn, json.dumps(report))


if __name__ == '__main__':
    privuy = PrivUY()
    try:
        privuy.start()    
    except Exception as err:
        print(err)
        privuy.driver.quit()  # gracefully terminate the process and have it gc'ed