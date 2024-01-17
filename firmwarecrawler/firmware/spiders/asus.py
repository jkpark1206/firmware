import re
from datetime import datetime
from random import uniform
from time import sleep
from time import timezone
from scrapy import Request, Spider
# from scrapy.loader import ItemLoader
#
# from firmware.items import FirmwareItem
from ..items import FirmwareImage
from ..loader import FirmwareLoader


'''class AsusSpider(Spider):
    name = 'asus'
    manufacturer = 'ASUS'
    device_dictionary = dict(
        gt='Router (Home)',  # Gaming
        rt='Router (Home)',
        rp='Repeater',
        ea='Access Point',
        ly='Router (Home)',  # Mesh
        bl='Router (Home)',  # Mesh
        ds='Router (Modem)',  # Modem
        pc='PCIe-Networkcard',
        us='USB-Networkcard',
        bt='Bluetooth-Adapter',
        br='Router (Business)',
        es='Server',
        rs='Server',
        ro='Router (Gaming)'  # ROG Rapture
    )
    base_url = 'https://www.asus.com/de/Networking-IoT-Servers/{}/All-series/filter/'
    start_urls = [
        base_url.format('WiFi-Routers'),
        base_url.format('Modem-Routers'),
        base_url.format('WiFi-6')
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 1.0,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def parse(self, response, **kwargs):
        url_redirects = set()
        header_scripts = set(response.xpath('//head//script/text()').getall())
        for header in header_scripts:
            if '"url"' not in header:
                continue
            url_redirects.update(re.findall(r'"url": "(https://[\w\d\-\_\./]+)"', header))
        for url_redirect in url_redirects:
            if url_redirect[-1] != '/':
                continue
            # selenium does not adhere to throttling settings, which is why we uniformly sleep to evade potential server-site throttling
            sleep(uniform(0.5, 2.0))
            yield Request(url=f'{url_redirect}HelpDesk_BIOS/', callback=self.parse_firmware, meta={'selenium': True}, cookies={"isReadCookiePolicyDNT": "Yes", "isReadCookiePolicyDNTAa":"true"})

    def parse_firmware(self, response):
        meta_data = self.prepare_meta_data(response)
        self.logger.debug(f"=================meta_data: {meta_data}")
        if meta_data['file_urls'] is None:
            return []
        return self.prepare_item_pipeline(response=response, meta_data=meta_data)

    @staticmethod
    def prepare_item_pipeline(response, meta_data):
        # item_loader_class = ItemLoader(item=FirmwareItem(), response=response, date_fmt=['%Y-%m-%d'])
        #
        # item_loader_class.add_value('device_name', meta_data['device_name'])
        # item_loader_class.add_value('vendor', meta_data['vendor'])
        # item_loader_class.add_value('firmware_version', meta_data['firmware_version'])
        # item_loader_class.add_value('device_class', meta_data['device_class'])
        # item_loader_class.add_value('release_date', meta_data['release_date'])
        # item_loader_class.add_value('file_urls', meta_data['file_urls'])
        item = FirmwareLoader(item=FirmwareImage(), response=response, date_fmt=['%Y-%m-%d'])
        item.add_value("version", meta_data['firmware_version'])
        item.add_value("url", meta_data['file_urls'])
        item.add_value("device_class", meta_data['device_class'])
        item.add_value("product", meta_data['device_name'])
        item.add_value("vendor", "asus")
        item.add_value("date", meta_data['release_date'])

        return item.load_item()

    def prepare_meta_data(self, response):
        # https://www.asus.com/de/networking-iot-servers/wifi-routers/asus-wifi-routers/rt-ax53u/helpdesk_bios?model2Name=RT-AX53U
        # https://www.asus.com/de/networking-iot-servers/wifi-routers/asus-wifi-routers/rt-ax53u/helpdesk_bios/

        # https://rog.asus.com/de/networking/rog-strix-gs-ax3000-model/helpdesk_bios/
        # https://rog.asus.com/support/webapi/product/GetPDBIOS?website=de&model=rog-strix-gs-ax3000&pdid=0&m1id=15543&cpu=&LevelTagId=197385&systemCode=rog
        # https://rog.asus.com/support/webapi/product/GetPDBIOS?website=de&model=rog-rapture-gt6-model&pdid=0&m1id=15543&cpu=&LevelTagId=197385&systemCode=rog
        info = response.xpath('//div[contains(@class,"ProductSupportDriverBIOS__fileTitle")]/text()').get()
        if not info:
            return {"file_urls": None}
        # ASUS 4G-N16 Firmware version 3.00.26_1.30
        # ASUS 4G-AC86U Modem Firmware version A21_02_001
        # ASUS ZenWiFi XD4 Plus Firmware version 3.0.0.4.386_69037
        # vendor, product_name, file_type, version_type, firmware_version = info.split(' ')
        firmware_version = info.split('version')[-1].strip()
        product_name = info.split('Firmware')[0].strip()
        return {
            'vendor': 'ASUS',
            'release_date': self.extract_release_date(response),
            'device_name': product_name,
            'firmware_version': firmware_version,
            'device_class': self.extract_device_class(response.url, product_name),
            'file_urls':
                response.xpath('//div[contains(@class,"ProductSupportDriverBIOS__contentRight")]//a/@href').get()
        }

    @staticmethod
    def extract_firmware_version(response):
        firmware_version = response.xpath('//div[contains(@class,"ProductSupportDriverBIOS__fileTitle")]/text()').get()
        return firmware_version.replace('Version', '').strip() if firmware_version else None

    @staticmethod
    def extract_release_date(response):
        release_date = response.xpath('//div[contains(@class,"ProductSupportDriverBIOS__releaseDate")]/text()').get()
        return datetime.strptime(release_date.strip(), '%Y/%m/%d').date().isoformat() if release_date else None

    def extract_device_class(self, response_url, product_name):
        if product_name and product_name[:2].lower() in self.device_dictionary:
            return self.device_dictionary[product_name[:2].lower()]
        if 'Motherboards' in response_url:
            return 'Motherboard'
        if 'Commercial' in response_url:
            return 'BIOS'
        return None  # undefined'''



