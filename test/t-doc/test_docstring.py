class Num:
    """
    数字类
    """
    def __init__(self, a, b):
        """
        构造
        """
        self.a = a
        self.b = b

    def add(self):
        """
        两束求和

        两数必须是整数
        """
        assert isinstance(self.a, int) and isinstance(self.b, int), "a,b需要为整数"
        return self.a+self.b

x = Num(1.2, 2)
x.add()
