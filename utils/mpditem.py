'''
作者: weimo
创建日期: 2021-01-01 15:15:12
上次编辑时间: 2021-01-01 15:41:08
一个人的命运啊,当然要靠自我奋斗,但是...
'''


class MPDItem:
    '''
    所有节点的父类
    '''
    def __init__(self, name: str = "MPDItem"):
        self.name = name
        self.childs = list()

    def addattr(self, name: str, value):
        self.__setattr__(name, value)

    def addattrs(self, attrs: dict):
        for attr_name, attr_value in attrs.items():
            attr_name: str
            attr_name = attr_name.replace(":", "_")
            self.addattr(attr_name, attr_value)