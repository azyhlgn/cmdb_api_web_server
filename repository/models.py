from django.db import models


# Create your models here.
class BusinessUnit(models.Model):
    # 业务线
    name = models.CharField('业务线', max_length=100, unique=True)

    class Meta:
        verbose_name = '业务线表'

    def __str__(self):
        return self.name


class IDC(models.Model):
    # 机房信息
    name = models.CharField('机房', max_length=100)
    floor = models.IntegerField('楼层', default=1)

    class Meta:
        verbose_name = '机房表'

    def __str__(self):
        return self.name + str(self.floor) + '层'


class Server(models.Model):
    # 服务器
    device_status_choices = (
        (1, '上架'),
        (2, '在线'),
        (3, '离线'),
        (4, '下架'),
    )
    device_status_id = models.IntegerField('设备状态', choices=device_status_choices, default=1)
    idc = models.ForeignKey('IDC', verbose_name='IDC机房', null=True, blank=True, on_delete=models.CASCADE)
    cabinet_num = models.CharField('机柜号', max_length=30, null=True, blank=True, )
    cabinet_order = models.CharField('机柜中序号', max_length=30, null=True, blank=True, )
    business_unit = models.ForeignKey('BusinessUnit', verbose_name='所属业务线', null=True, blank=True,
                                      on_delete=models.CASCADE)

    # 基本信息
    hostname = models.CharField('主机名称', max_length=128, unique=True)
    os_platform = models.CharField('主机系统', max_length=16, null=True, blank=True, )
    os_version = models.CharField('主机系统版本', max_length=16, null=True, blank=True, )

    # dmidecode -t1 命令可以查看到
    sn = models.CharField('主板SN号', max_length=64, db_index=True)
    manufacture = models.CharField(verbose_name='主板制造商', max_length=64, null=True, blank=True, )
    model = models.CharField('主板型号', max_length=64, null=True, blank=True, )
    # cat /proc/cpuinfo 命令收集查看
    cpu_count = models.IntegerField('CPU个数', null=True, blank=True, )
    cpu_physical_count = models.IntegerField('CPU物理个数', null=True, blank=True, )
    cpu_model = models.CharField('CPU型号', max_length=128, null=True, blank=True, )

    latest_data = models.DateField('最后更新时间', null=True, auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        verbose_name = '服务器表'

    def __str__(self):
        return self.hostname


class Disk(models.Model):
    # 硬盘信息  MegaCli -PDList -aAll 命令有点问题 之后在看 中控机有一个shell脚本可以生成同格式的结果
    slot = models.CharField('硬盘槽位', max_length=8)
    model = models.CharField('硬盘型号', max_length=32)
    capacity = models.CharField('硬盘容量GB', null=True, blank=True)
    pd_type = models.CharField('硬盘类型', max_length=32)

    server = models.ForeignKey(verbose_name='服务器', to='Server', related_name='disk', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '硬盘表'

    def __str__(self):
        return self.slot


class NIC(models.Model):
    # 网卡    ip -o link show    ip -o addr show  查看
    name = models.CharField('网卡名称', max_length=128)
    hwaddr = models.CharField('网卡mac名称', max_length=64)
    ipaddrs_netmask = models.CharField('网卡ip地址和子网掩码', max_length=256)
    up = models.BooleanField('网卡状态',default=False)
    server = models.ForeignKey('Server', related_name='nic_list', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '网卡表'

    def __str__(self):
        return self.name


class Memory(models.Model):
    # 内存信息  dmidecode -q -t 17 2>/dev/null 命令查看
    slot = models.CharField('内存槽位', max_length=32)
    manufacture = models.CharField(verbose_name='内存制造商', max_length=32, null=True, blank=True, )
    model = models.CharField('内存型号', max_length=64)
    capacity = models.CharField('内存容量GB', null=True, blank=True, )
    sn = models.CharField('内存SN号', max_length=64, db_index=True)
    speed = models.CharField('内存速度', max_length=16, null=True, blank=True, )

    server = models.ForeignKey(verbose_name='服务器', to='Server', related_name='memory_list', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '硬盘表'

    def __str__(self):
        return self.slot


class Asset(models.Model):
    # 资产变更记录 creator为空表示是资产汇报的数据
    server = models.ForeignKey('Server', related_name='servers', on_delete=models.CASCADE)
    content = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '资产记录表'


class ErrorLog(models.Model):
    server = models.ForeignKey('Server', null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=16)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '错误日志表'

    def __str__(self):
        return self.title
