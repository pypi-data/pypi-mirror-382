from faker import Faker
import string
import time
import random
import datetime
import pytz
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode, urlparse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from cloud.CloudRequestUtil import CloudHttpClient


class CloudTimes:
    def __init__(self, dt=None, tz=pytz.timezone('Asia/Shanghai')):
        """
        初始化时间工具类

        :param dt: datetime对象，默认使用当前时间
        :param tz: 时区，默认使用本地时区
        """
        self.tz = tz
        self.dt = dt or datetime.datetime.now(self.tz)

    def to_datetime(self):
        """
        返回datetime对象

        :return: datetime对象
        """
        return self.dt

    def to_str(self, fmt='%Y-%m-%dT%H:%M:%SZ'):
        """
        将datetime对象转换为指定格式的字符串

        :param fmt: 时间格式，默认为'%Y-%m-%d %H:%M:%S'
        :return: 格式化后的时间字符串
        """
        return self.dt.strftime(fmt)


class CloudDataGenerator:
    """
    生成中文数据的工具类
    """
    
    # 类级别的计数器，确保cno绝对唯一
    _cno_counter = 0

    def __init__(self):
        self.fake = Faker(locale='zh_CN')

    def generate_name(self):
        """
        生成中文姓名，返回字符串。
        """
        return self.fake.name()

    def generate_address(self):
        """
        生成中文地址，返回字符串。
        """
        return self.fake.address()

    def generate_phone_number(self):
        """
        生成中文手机号，返回字符串。
        """
        return self.fake.phone_number()

    def generate_id_number(self):
        """
        生成中文身份证号码，返回字符串。
        """
        return self.fake.ssn()

    def random_number(self, digits=4):
        """
        生成一个指定位数的随机整数并转换为字符串类型
        如果生成的整数不足指定位数，则在左侧用0进行填充
        """
        digits = int(digits)
        return f"{{:0{digits}d}}".format(self.fake.random_number(digits=digits))
    
    def generate_cno(self, min_digits=3, max_digits=10):
        """
        生成3-10位纯数字的cno，确保一次运行中不重复
        使用UUID+时间戳+计数器确保绝对唯一性，避免以0开头
        
        Args:
            min_digits (int): 最小位数，默认3
            max_digits (int): 最大位数，默认10
            
        Returns:
            str: 生成的cno字符串
        """
        import uuid
        import time
        
        # 增加计数器确保绝对唯一性
        CloudDataGenerator._cno_counter += 1
        
        # 生成随机位数（3-10位）
        digits = random.randint(min_digits, max_digits)
        
        # 生成UUID并转换为数字
        uuid_str = uuid.uuid4().hex
        # 取UUID的前12位转换为数字
        uuid_num = int(uuid_str[:12], 16)
        
        # 添加时间戳确保唯一性（纳秒级精度）
        timestamp = int(time.time() * 1000000000)  # 纳秒级时间戳
        
        # 添加计数器确保绝对唯一性
        counter = CloudDataGenerator._cno_counter
        
        # 组合生成唯一数字
        unique_num = (uuid_num + timestamp + counter) % (10 ** 15)  # 限制在15位以内
        
        # 确保数字在指定位数范围内且不以0开头
        min_value = 10 ** (digits - 1)  # 最小n位数（不以0开头）
        max_value = 10 ** digits - 1    # 最大n位数
        
        # 如果超出范围则取模
        if unique_num > max_value:
            unique_num = min_value + (unique_num % (max_value - min_value + 1))
        elif unique_num < min_value:
            unique_num = min_value + (unique_num % (max_value - min_value + 1))
        
        return str(unique_num)
    
    def generate_cno_range(self, start_digits=3, end_digits=10, count=1):
        """
        生成cno范围，用于批量操作
        确保endCno > cno且位数一致
        
        Args:
            start_digits (int): 起始位数，默认3
            end_digits (int): 结束位数，默认10
            count (int): 生成数量，默认1
            
        Returns:
            tuple: (start_cno, end_cno) 起始和结束cno
        """
        # 生成随机位数
        digits = random.randint(start_digits, end_digits)
        
        # 生成起始cno
        start_cno = self.generate_cno(digits, digits)
        
        # 计算结束cno
        start_value = int(start_cno)
        end_value = start_value + count - 1
        
        # 确保结束值不超过指定位数的最大值
        max_value = 10 ** digits - 1
        if end_value > max_value:
            # 如果超出范围，重新生成起始值
            start_value = max_value - count + 1
            start_cno = str(start_value)
            end_value = max_value
        
        end_cno = str(end_value)
        
        return start_cno, end_cno
    
    def generate_cno_fixed_digits(self, digits):
        """
        生成指定位数的cno，保持向后兼容性
        
        Args:
            digits (int): 指定位数
            
        Returns:
            str: 生成的cno字符串
        """
        return self.generate_cno(digits, digits)

    def get_cloud_password(self):
        """
        获取初始化的SK 加密后的密码
        :return:
        """
        # 这里不能直接引用config，因为config类还没有定义
        # 在实际使用时，会通过实例方法调用
        return "default_cloud_password"

    @staticmethod
    def start_of_day():
        """
        获取当前时间开始时间戳：eg：2023-06-01 00:00:00
        """
        now = datetime.datetime.now()
        return datetime.datetime(now.year, now.month, now.day)

    @staticmethod
    def end_of_day():
        """
        获取当前时间开始时间戳：eg：2023-06-01 23:59:59
        """
        return CloudDataGenerator.start_of_day() + datetime.timedelta(days=1) - datetime.timedelta(seconds=1)

    def start_of_day_s(self):
        """
        获取当前时间开始时间戳：eg：1685548800  秒级
        """
        return int(time.mktime(CloudDataGenerator.start_of_day().timetuple()))

    def end_of_day_s(self):
        """
        获取当前时间结束时间戳：eg：1685635199 秒级
        """
        return int(time.mktime(CloudDataGenerator.end_of_day().timetuple()))

    def random_externalId(self):
        """
        生成唯一性数据，crm用于 外部企业客户id
        """
        num = str(random.randint(1000, 9999))
        src_uppercase = string.ascii_uppercase  # string_大写字母
        src_lowercase = string.ascii_lowercase  # string_小写字母
        chrs = random.sample(src_lowercase + src_uppercase, 3)
        for i in chrs:
            num += i
        return num
    
    def encryptPassword(self, plain_text='Aa112233'):
        """
        加密 - 使用默认密钥
        """
        # 使用默认密钥进行加密
        password = "default_encryption_key"
        # 设置随机数生成器的种子
        secure_random = hashlib.sha1(password.encode()).digest()
        # 创建对称加密密钥生成器
        kgen = hashlib.sha1(secure_random).digest()[:16]
        # 创建密码器并初始化
        cipher = AES.new(kgen, AES.MODE_ECB)
        # 加密明文（使用PKCS7填充）
        padded_plain_text = pad(plain_text.encode(), AES.block_size)
        encrypted_bytes = cipher.encrypt(padded_plain_text)
        # 将加密结果转换为16进制字符串
        encrypted_text = base64.b16encode(encrypted_bytes).decode().lower()
        return encrypted_text

    def decrypt(self, encrypted_text, password):
        """
        # 解密
        """
        # 设置随机数生成器的种子
        secure_random = hashlib.sha1(password.encode()).digest()
        # 创建对称加密密钥生成器
        kgen = hashlib.sha1(secure_random).digest()[:16]
        # 创建密码器并初始化
        cipher = AES.new(kgen, AES.MODE_ECB)
        # 解密密文（parseHexStr2Byte方法为将16进制字符串转为二进制字节数组）
        encrypted_bytes = base64.b16decode(encrypted_text)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        decrypted_text = unpad(decrypted_bytes, AES.block_size).decode()
        return decrypted_text

    def generate_user_data(self):
        """
        生成随路数据JSON字符串
        格式：{"key":"value"}，不支持数组和嵌套
        """
        data = {
            "testKey1": f"testValue{self.fake.random_number(digits=3)}",
            "testKey2": f"testValue{self.fake.random_number(digits=3)}",
            "testKey3": f"testValue{self.fake.random_number(digits=3)}"
        }
        return json.dumps(data, ensure_ascii=False)
    
    def generate_user_data_keys(self):
        """
        生成随路数据键值字符串
        格式：key1,key2,key3
        """
        return "testKey1,testKey2,testKey3"

    def generate_cloud_signature(self, method, url, params, access_key_id, access_key_secret):
        """
        生成云服务签名
        """
        # 获取当前时间戳
        timestamp = int(time.time())
        
        # 构建签名字符串
        # 1. 请求方法
        string_to_sign = method.upper() + "\n"
        
        # 2. 请求路径
        parsed_url = urlparse(url)
        string_to_sign += parsed_url.path + "\n"
        
        # 3. 查询参数（按字典序排序）
        if params:
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{k}={v}" for k, v in sorted_params])
            string_to_sign += query_string + "\n"
        else:
            string_to_sign += "\n"
        
        # 4. 时间戳
        string_to_sign += str(timestamp)
        
        # 使用HMAC-SHA256进行签名
        signature = hmac.new(
            access_key_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # 构建Authorization头
        auth_header = f"Cloud {access_key_id}:{signature}"
        
        return auth_header, timestamp


class config:
    """
    配置文件
    """

    def __init__(self, baseUrl=None, token=None, CloudPassword=None, 
                 commonTestCasePath=None, methObj=None, Session: CloudHttpClient = CloudHttpClient(), 
                 assertFail='stop', tEnv='base', enterpriseId=None, validateType='2', obClids=None):
        """
        初始化配置文件
        """
        self._baseUrl = baseUrl
        self._token = token
        self._enterpriseId = enterpriseId
        self._validateType = validateType
        # 加密后的密码
        self._CloudPassword = CloudPassword
        self._commonTestCasePath = commonTestCasePath
        self._methObj = methObj
        self._assertFail = assertFail
        self._tEnv = tEnv
        # 构建全局session
        self._Session = Session
        # 外呼号码配置
        self._obClids = obClids

    @property
    def Session(self):
        return self._Session

    @Session.setter
    def Session(self, value):
        self._Session = value

    @property
    def methObj(self):
        return self._methObj

    @methObj.setter
    def methObj(self, value):
        self._methObj = value

    @property
    def CloudPassword(self):
        return self._CloudPassword

    @CloudPassword.setter
    def CloudPassword(self, value):
        self._CloudPassword = value

    @property
    def commonTestCasePath(self):
        return self._commonTestCasePath

    @commonTestCasePath.setter
    def commonTestCasePath(self, value):
        self._commonTestCasePath = value

    @property
    def baseUrl(self):
        return self._baseUrl

    @baseUrl.setter
    def baseUrl(self, value):
        self._baseUrl = value

    @property
    def assertFail(self):
        return self._assertFail

    @assertFail.setter
    def assertFail(self, value):
        self._assertFail = value

    @property
    def enterpriseId(self):
        return self._enterpriseId

    @enterpriseId.setter
    def enterpriseId(self, value):
        self._enterpriseId = value

    @property
    def tEnv(self):
        return self._tEnv

    @tEnv.setter
    def tEnv(self, value):
        self._tEnv = value

    @property
    def validateType(self):
        return self._validateType

    @validateType.setter
    def validateType(self, value):
        self._validateType = value

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, value):
        self._token = value

    @property
    def obClids(self):
        return self._obClids

    @obClids.setter
    def obClids(self, value):
        self._obClids = value