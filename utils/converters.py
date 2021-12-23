class UsernameConverter:
    """自定义路由转换器去匹配用户名"""
    # 定义匹配用户名的正则表达式
    # 2-6个任意字符(包括中文)，需要注意的是传入的用户名有中文时，在插入数据库的时候需要进行编码，取出时需要解码
    # 字符串前面加u表明字符串含有中文
    regex = u'[(a-zA-Z0-9-_~;:+,\\*/)|(\u4e00-\u9fa5)]{2,6}'

    def to_python(self, value):
        return str(value)


class PhoneConverter:
    """自定义路由转换器去匹配手机号"""
    # 定义匹配手机号的正则表达式
    regex = '1(?:3\\d|4[4-9]|5[0-35-9]|6[67]|7[013-8]|8\\d|9\\d)\\d{8}'

    def to_python(self, value):
        return str(value)