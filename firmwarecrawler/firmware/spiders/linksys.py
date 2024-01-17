from scrapy import Spider
from scrapy.http import Request, HtmlResponse

from ..items import FirmwareImage
from ..loader import FirmwareLoader

import urllib.request, urllib.parse, urllib.error

# see: http://www.dd-wrt.com/phpBB2/viewtopic.php?t=145255&postdays=0&postorder=asc&start=0
# and http://download.modem-help.co.uk/mfcs-L/LinkSys/


class LinksysSpider(Spider):
    name = "linksys"
    allowed_domains = ["linksys.com"]
    start_urls = ["https://www.linksys.com/sitemap"]

    def parse(self, response):
        for link in response.xpath("//a[@class='sitemap-list__link']/@href").extract():
            self.logger.debug(link)
            yield Request(
                url=urllib.parse.urljoin(response.url, link),
                headers={"Referer": response.url},
                callback=self.parse_support)

    def parse_support(self, response):
        for link in response.xpath("//a[@title='DOWNLOADS / FIRMWARE']"):
            href = link.xpath("@href").extract()[0]
            dsp = response.xpath("//div[@class='product-family-name h3']/text()").extract()[0].replace("\r\n", '').strip()
            product = response.xpath("//span[@class='product-id']/text()").extract()[0]
            self.logger.debug(f"1======href:{href}, desp:{dsp}, product:{product}")
            yield Request(
                url=href,
                meta={"product": product, "description": dsp},
                headers={"Referer": response.url},
                callback=self.parse_kb)

    def parse_kb(self, response):
        version_divs = response.xpath('//div[@class="article-accordian-content collapse-me"]')
        for version_div in version_divs:
            url_list = list(set([one for one in version_div.xpath('p/a/@href').extract() if not one.endswith('txt')]))
            ver_list = version_div.xpath('p/span/text()').extract()
            if not ver_list:
                ver_list = version_div.xpath('p/text()').extract()
            version_list = []
            for ver in ver_list:
                if "Version:" in ver:
                    version_list.append(ver.replace('Version:', '').strip())
                elif 'Ver.' in ver:
                    version_list.append(ver.replace('Ver.', '').strip())

            for i, url in enumerate(url_list):
                try:
                    version = version_list[i]
                except:
                    version = ''
                self.logger.debug(f"2======version:{version}, url:{url}")
                if url.endswith('exe'):
                    continue
                item = FirmwareLoader(item=FirmwareImage(), response=response)
                item.add_value("date", '')
                item.add_value("url", url)
                # item.add_value("url", url)
                item.add_value("product", response.meta['product'])
                item.add_value("vendor", self.name)
                item.add_value("device_class", response.meta["description"])
                item.add_value("version", version)
                yield item.load_item()

