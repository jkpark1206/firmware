#coding:utf-8
#note: 官网bug，升级软件栏目只能打开一页
from scrapy import Spider
from scrapy.http import Request

from ..items import FirmwareImage
from ..loader import FirmwareLoader
import string
import json
import urllib.request, urllib.parse, urllib.error


class TendaZHSpider(Spider):
    name = "tenda_zh"
    vendor = "tenda"
    allowed_domains = ["www.tenda.com.cn"]
    start_urls = ["https://www.tenda.com.cn/download/detail-3811.html"]
    base_url = "http://www.tenda.com.cn/{}"

    def parse(self, response):
        start_urls = [f"https://www.tenda.com.cn/download/detail-{i}.html" for i in range(1777, 3811)]
        for url in start_urls:
            yield Request(
                url=url,
                callback=self.parse_product)

    def parse_product(self, response):
        # table = response.xpath("//table[@class='table']")
        # a = response.xpath('//strong[contains(text(),"文件名称：")][1]').extract()
        a = response.xpath('//div[@class="btnDown onebtn"]/a/@href').extract()
        b = response.xpath('//table[@class="table"]/tr/td/text()').extract()
        c = response.xpath('//table[@class="table"]/tr/td/a/text()').extract()
        # self.logger.debug(f"===============a:{a}, b:{b}, c:{c}")
        if a and b and c:
            b_clean = []
            for item in b:
                if item != "\r\n" or item != '\t':
                    b_clean.append(item)
            dsp = b_clean[0]
            version = b_clean[1].strip()
            date = b_clean[2]
            product = c[0]
            download_url = urllib.parse.quote(f"https:{a[0]}", safe=string.printable).replace(" ", "%20")
            if "升级文件" in dsp or "升级软件" in dsp or "驱动" in dsp:
                self.logger.debug(f"===============dsp:{dsp}, version:{version}, date:{date}, product:{product}, download_url:{download_url}")
                item = FirmwareLoader(
                    item=FirmwareImage(), response=response)
                item.add_value("version", version)
                item.add_value("url", download_url)
                item.add_value("product", product)
                item.add_value("vendor", self.vendor)
                item.add_value("date", date)
                yield item.load_item()
