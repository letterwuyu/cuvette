class SingletonType(type):
    def __init__(self,*args,**kwargs):
        super(SingletonType,self).__init__(*args,**kwargs)

    def __call__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super(SingletonType,cls).__call__(*args, **kwargs)
        return cls._instance
