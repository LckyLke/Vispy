from base import Base

class Derived(Base):
    def derived_method(self):
        pass

    def shared_method(self):
        pass

    def __init__(self):
        super().__init__()
        self.derived_var = 3
        self.shared_var = 4
