#coding:utf-8
from scrapy import Spider
from scrapy.http import Request

from ..items import FirmwareImage
from ..loader import FirmwareLoader

import re
import urllib.request, urllib.parse, urllib.error
import logging

class NetcoreSpider(Spider):
    name = "netcore"
    allowed_domains = ["netcoretec.com"]
    url_base = "https://www.netcoretec.com/service-support/download/firmware/{}.html"
    start_urls = []
    for i in range(311, 2680):
        full_url = url_base + str(i+1)
        start_urls.append(url_base.format(i))
    #start_urls = ["http://www.netcoretec.com/portal/list/index/id/12.html?id=12&page=2"]
    # product_url = 'http://www.netcoretec.com/upload/'
    # firmware_url = "http://www.netcoretec.com/"

    def parse(self, response):
        desp = response.xpath('//h1[@class="detail-title fz-36 black27 comm-title mt-80 lts-30"]/text()').extract()[0]
        url = response.xpath('//a[@class="btn-go fz-14 blue download mt-20"]/@href').extract()[0]
        product = desp.split('-')[0] if '-' in desp else ''
        item = FirmwareLoader(item=FirmwareImage(), response=response)
        item.add_value("date", '')
        item.add_value("description",  desp)
        item.add_value("url", f"https://www.netcoretec.com{url}")
        item.add_value("product", product if product.lower() != self.name else desp.split('-')[1])
        item.add_value("vendor", self.name)
        yield item.load_item()
