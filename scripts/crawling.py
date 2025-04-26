import asyncio
import aiohttp  # Install with "pip install aiohttp".
from asyncio import Queue

import cgi
from collections import namedtuple
import logging
import re
import time
import urllib.parse
from urllib.parse import urljoin

FetchStatistic = namedtuple('FetchStatistic', [
    'url', 'next_url', 'status', 'exception', 'size', 'content_type',
    'encoding', 'num_urls', 'num_new_urls'
])


def lenient_host(host):
    parts = host.split('.')[-2:]
    return ''.join(parts)


def is_redirect(response):
    return response.status in (300, 301, 302, 303, 307)


class Crawler:
    def __init__(
            self,
            roots,
            exclude=None,
            strict=True,  # What to crawl.
            max_redirect=10,
            max_tries=4,  # Per-url limits.
            max_tasks=10):
        self.roots = roots  # 使用者指定抓取的網站地址，是一個 list
        self.exclude = exclude
        self.strict = strict
        self.max_redirect = max_redirect
        self.max_tries = max_tries
        self.max_tasks = max_tasks
        self.seen_urls = set()  # 會保證不重複 url 與和已經抓取過的 url
        self.done = []
        self.root_domains = set()

    # 解析爬取到的 url 是否符合需求規範
    def host_okay(self, host):
        """Check if a host should be crawled.

        A literal match (after lowercasing) is always good.  For hosts
        that don't look like IP addresses, some approximate matches
        are okay depending on the strict flag.
        """
        host = host.lower()
        if host in self.root_domains:
            return True
        if re.match(r'\A[\d\.]*\Z', host):
            return False
        if self.strict:
            return self._host_okay_strictish(host)
        else:
            return self._host_okay_lenient(host)

    def _host_okay_strictish(self, host):
        """Check if a host should be crawled, strict-ish version.

        This checks for equality modulo an initial 'www.' component.
        """
        host = host[4:] if host.startswith('www.') else 'www.' + host
        return host in self.root_domains

    def _host_okay_lenient(self, host):
        """Check if a host should be crawled, lenient version.

        This compares the last two components of the host.
        """
        return lenient_host(host) in self.root_domains

    def url_allowed(self, url):
        if self.exclude and re.search(self.exclude, url):
            print('--------------------exclude', url)
            return False
        parts = urllib.parse.urlparse(url)
        if parts.scheme not in ('http', 'https'):
            return False
        host = parts.hostname
        if not self.host_okay(host):
            return False
        return True

    # 將爬取到的 url 放入列隊
    def add_url(self, url, max_redirect=None):
        # print(url)
        if max_redirect is None:
            max_redirect = self.max_redirect
        self.seen_urls.add(url)
        self.q.put_nowait((url, max_redirect))

    def record_statistic(self, fetch_statistic):
        """Record the FetchStatistic for completed / failed URL."""
        self.done.append(fetch_statistic)

    # 以下為主要運行的異步函式
    # Step 5
    async def parse_links(self, response):
        links = set()
        content_type = None
        encoding = None
        body = await response.read()
        if response.status == 200:
            content_type = response.headers.get('content-type')
            pdict = {}

            if content_type:
                content_type, pdict = cgi.parse_header(content_type)
            encoding = pdict.get('charset', 'utf-8')
            if content_type in ('text/html', 'application/xml'):
                text = await response.text()

                urls = set(re.findall(r'''(?i)href=["']([^\s"'<>]+)''', text))
                for url in urls:
                    url_join = urllib.parse.urljoin(str(response.url), url)
                    defragmented, frag = urllib.parse.urldefrag(url_join)
                    if self.url_allowed(defragmented):
                        links.add(defragmented)
                        print(defragmented)

        stat = FetchStatistic(url=response.url,
                              next_url=None,
                              status=response.status,
                              exception=None,
                              size=len(body),
                              content_type=content_type,
                              encoding=encoding,
                              num_urls=len(links),
                              num_new_urls=len(links - self.seen_urls))

        return stat, links

    # Step 4
    async def fetch(self, url, max_redirect):
        tries = 0
        exception = None
        while tries < self.max_tries:
            # 取得 url 的 response，失敗則在 max_tries 內持續嘗試
            try:
                response = await self.session.get(url, allow_redirects=False)
                break
            except Exception as e:
                exception = e
            tries += 1
        else:
            self.record_statistic(
                FetchStatistic(url=url,
                               next_url=None,
                               status=None,
                               exception=exception,
                               size=0,
                               content_type=None,
                               encoding=None,
                               num_urls=0,
                               num_new_urls=0))
            return
        try:
            # 判斷是否跳轉頁面
            if is_redirect(response):
                location = response.headers['location']
                next_url = urllib.parse.urljoin(url, location)
                self.record_statistic(
                    FetchStatistic(url=url,
                                   next_url=next_url,
                                   status=response.status,
                                   exception=None,
                                   size=0,
                                   content_type=None,
                                   encoding=None,
                                   num_urls=0,
                                   num_new_urls=0))

                if next_url in self.seen_urls:
                    return
                if max_redirect > 0:
                    self.add_url(next_url, max_redirect - 1)
                else:
                    print('redirect limit reached for %r from %r', next_url,
                          url)
            else:
                stat, links = await self.parse_links(response)

                self.record_statistic(stat)
                for link in links.difference(self.seen_urls):
                    self.q.put_nowait((link, self.max_redirect))
                self.seen_urls.update(links)
        finally:
            await response.release()

    # Step 3
    async def work(self):
        try:
            while True:
                url, max_redirect = await self.q.get()
                await self.fetch(url, max_redirect)
                self.q.task_done()

        except asyncio.CancelledError:
            pass

    # Step 2
    async def crawl(self):
        self.q = asyncio.Queue()  # 存放所有等待抓取的 url
        self.t0 = time.time()
        self.session = aiohttp.ClientSession()

        for root in self.roots:
            parts = urllib.parse.urlparse(root)
            host = parts.hostname

            # 判斷解析 url 後有無 host
            if not host:
                continue
            # 判斷 host 是否為數字
            if re.match(r'\A[\d\.]*\Z', host):
                self.root_domains.add(host)
            else:
                host = host.lower()
                if self.strict:
                    self.root_domains.add(host)
                else:
                    self.root_domains.add(lenient_host(host))

        for root in self.roots:
            self.add_url(root)

        workers = [
            asyncio.create_task(self.work()) for _ in range(self.max_tasks)
        ]

        await self.q.join()  # 等待列隊 url 清空，將結束任務

        for w in workers:
            w.cancel()

        await self.session.close()

        self.t1 = time.time()

# Step 1
time_start = time.time()
crawler = Crawler(['https://xkcd.com'], max_tasks=30, exclude='.css')
asyncio.run(crawler.crawl())

print(len(crawler.done))
print(time.time() - time_start)