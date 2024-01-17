from django.db import models


class BaseModel(models.Model):
    """模型抽象基类"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="删除标记")

    class Meta:
        abstract = True


class Firmware(BaseModel):
    """

    """
    vendor = models.CharField(max_length=100, verbose_name="厂商")
    url = models.CharField(max_length=500, verbose_name="下载地址")
    url_hash = models.CharField(max_length=100, db_index=True, verbose_name="下载地址hash")
    description = models.CharField(max_length=500, verbose_name="描述说明")
    product = models.CharField(max_length=100, verbose_name="型号")
    version = models.CharField(max_length=100, verbose_name="固件版本")
    device_class = models.CharField(max_length=100, verbose_name="设备类型")
    file_path = models.CharField(max_length=500, unique=True, verbose_name="固件路径")
    is_send = models.BooleanField(default=False, verbose_name="是否发送易识创建分析任务")

    def __str__(self):
        return self.file_path


