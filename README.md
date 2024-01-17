# firmware crawler 固件爬虫

本项目主要用于爬取网络设备固件，如路由器、网络摄像头、交换机等。并将爬取的固件通过api接口创建易识固件分析任务。

## 开启爬虫下载固件

厂商包括: 360,belkin,camius,hikvision,linksys,mikrotik,netgear,routertech,tenda_en,tenvis,tp-link_en,trendnet,ublox,
avm,buffalo,dlink,mercury,netcore,openwrt,qnap,supermicro,tenda_zh,tomato-shibby,tp-link_zh-cn,ubiquiti,zyxel

```
scrapy crawl dlink
```

## 创建用户

```
python manage.py createsuperuser
```

## 开启web服务
```
python3 manage.py runserver

# http://127.0.0.1:8000/admin/
```

## 批量将固件导入易识创建固件分析任务
```
python manage.py send_ys
```
