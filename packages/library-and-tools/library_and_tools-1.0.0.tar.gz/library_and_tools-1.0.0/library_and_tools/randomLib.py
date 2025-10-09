import random

__all__ = [
    "seed",
    "getstate",
    "setstate",
    "getrandbits",
    "randrange",
    "randint",
    "choice",
    "choices",
    "shuffle",
    "sample",
    "random_float",
    "uniform",
    "triangular",
    "betavariate",
    "expovariate",
    "gammavariate",
    "gauss",
    "lognormvariate",
    "normalvariate",
    "vonmisesvariate",
    "paretovariate",
    "weibullvariate"
]


# === الأوامر الأساسية ===

def seed(a=None, version=2):
    """تهيئة مولد الأرقام العشوائية"""
    random.seed(a, version)

def getstate():
    """ترجع حالة المولد الحالية"""
    return random.getstate()

def setstate(state):
    """تسترجع حالة المولد"""
    random.setstate(state)

def getrandbits(k):
    """ترجع عدد عشوائي من k بت"""
    return random.getrandbits(k)

def randrange(start, stop=None, step=1):
    """ترجع رقم عشوائي من range محدد"""
    return random.randrange(start, stop, step)

def randint(a, b):
    """ترجع رقم صحيح عشوائي بين a و b (يشملهم)"""
    return random.randint(a, b)

def choice(seq):
    """ترجع عنصر عشوائي من تسلسل (list, tuple, string...)"""
    return random.choice(seq)

def choices(population, weights=None, *, cum_weights=None, k=1):
    """ترجع قائمة بعناصر عشوائية مع احتمالات محددة"""
    return random.choices(population, weights=weights, cum_weights=cum_weights, k=k)

def shuffle(seq):
    """تخلط العناصر داخل القائمة"""
    random.shuffle(seq)
    return seq

def sample(population, k, *, counts=None):
    """تختار k عناصر بدون تكرار من قائمة"""
    return random.sample(population, k, counts=counts)

def random_float():
    """ترجع رقم عشوائي عشري بين 0 و 1"""
    return random.random()

def uniform(a, b):
    """ترجع رقم عشوائي عشري بين a و b"""
    return random.uniform(a, b)

def triangular(low=0.0, high=1.0, mode=None):
    """توزيع ثلاثي"""
    return random.triangular(low, high, mode)

def betavariate(alpha, beta):
    """توزيع بيتا"""
    return random.betavariate(alpha, beta)

def expovariate(lambd):
    """توزيع أسي"""
    return random.expovariate(lambd)

def gammavariate(alpha, beta):
    """توزيع جاما"""
    return random.gammavariate(alpha, beta)

def gauss(mu, sigma):
    """توزيع جاوسي (عادي)"""
    return random.gauss(mu, sigma)

def lognormvariate(mu, sigma):
    """توزيع لوغاريتمي طبيعي"""
    return random.lognormvariate(mu, sigma)

def normalvariate(mu, sigma):
    """توزيع طبيعي"""
    return random.normalvariate(mu, sigma)

def vonmisesvariate(mu, kappa):
    """توزيع فون ميسس"""
    return random.vonmisesvariate(mu, kappa)

def paretovariate(alpha):
    """توزيع باريتو"""
    return random.paretovariate(alpha)

def weibullvariate(alpha, beta):
    """توزيع ويبول"""
    return random.weibullvariate(alpha, beta)

# === alias بسيط لسهولة الاستخدام ===
def random():
    """ترجع رقم عشوائي عشري بين 0 و 1"""
    return random.random()
    
