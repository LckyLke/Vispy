class ClassA:
    def method_shared_all(self):
        pass

    def method_shared_ab(self):
        pass

    def method_unique_a(self):
        pass

    def __init__(self):
        self.var_shared_all = 1
        self.var_shared_ab = 2
        self.var_unique_a = 3

class ClassB:
    def method_shared_all(self):
        pass

    def method_shared_ab(self):
        pass

    def method_unique_b(self):
        pass

    def __init__(self):
        self.var_shared_all = 1
        self.var_shared_ab = 2
        self.var_unique_b = 4

class ClassC:
    def method_shared_all(self):
        pass

    def method_unique_c(self):
        pass

    def __init__(self):
        self.var_shared_all = 1
        self.var_unique_c = 5
