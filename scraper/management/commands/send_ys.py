from django.core.management import BaseCommand
import os
from scraper.models import Firmware
import requests
from jsonpath import jsonpath
import os
import hashlib
import json

#v2.11 分析策略
# URL ='http://192.168.5.242:8011/'
URL ='http://192.168.1.186:8011/'
ROOT_PATH = os.path.abspath('./output')


def Get_file_md5(file_path):
    try:
        with open(file_path,'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            hash_value = md5obj.hexdigest()
            return hash_value
    except Exception as e:
        print('ERROR', f'获取文件{file_path}md5值出错,原因{e}')
        return False


class Command(BaseCommand):
    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout, stderr, no_color, force_color)
        self.session = requests.session()
        data = {"username": 'wwh',
                "password": '126cfbcd4d16ae6d25c9bfcae76d8ee4',
                "anban_password": '6b5c557da96612408d2844af0d9f5e5d'}
        headers = {"Content-Type": "application/json"}
        res = self.session.post('{}api/user/login'.format(URL), json=data, headers=headers)
        self.token = 'Token ' + jsonpath(res.json(), '$.data.AuthToken')[0]

    def handle(self, *args, **options):
        firmwares = Firmware.objects.filter(is_send=False).order_by('id')
        for firmware in firmwares:
            # TODO 以下三个字段接口暂未开放
            # vendor = firmware.vendor  # 厂商
            # version = firmware.version  # 固件版本
            # device_class = firmware.device_class  # 设备类型
            firm_path = os.path.join(ROOT_PATH, firmware.file_path)
            if not os.path.exists(firm_path):
                continue
            file_md5 = Get_file_md5(os.path.join(firm_path))
            h = {"Authorization": self.token}
            d = {
                "file_md5": file_md5,
                "strategy_id": 1
            }
            file_size = os.path.getsize(firm_path) / 1024 / 1024 / 1024
            if file_size > 5:  # 过滤超过5GB的固件，需要上传5GB以下的固件，反之即可
                continue
            else:
                with open(firm_path, 'rb') as file:
                    f = {'firmware': file}
                    res2 = self.session.post('{}api/task/create'.format(URL), data=d, headers=h, files=f)
                    task_id = json.loads(res2.text)["data"]["id"]
                    d2 = {"task_id": task_id}
                    res3 = self.session.put('{}api/task/start'.format(URL), json=d2, headers=h)
                    print(res3.text)
                # 创建分析任务成功就修改标志位
                firmware.is_send = True
                firmware.save(update_fields=['is_send'])


