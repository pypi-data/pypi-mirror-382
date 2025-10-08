from enum import Enum, auto

class Transform(Enum):

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

    def __str__(self):
        return '%s' % self.name

    No_Transform = auto()
    Square_Root = auto()
    Natural_Log = auto()
    Base_10_Log = auto()
    Inverse_Sqrt = auto()
    Inverse = auto()
    Power = auto()
    Logit = auto()
    ArcSin_Sqrt = auto()
    Logistic = auto()
    Poisson = auto()
    Gaussian_Process = auto()
