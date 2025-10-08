from ..feature import KitFeature



class UseCreateFuncReader:
    
    pass

class Feature(KitFeature):
    
    def __init__(self, target_dir, backend_dir):
        feature_type = 'django_from_usecreatefunc'
        super().__init__(target_dir=target_dir, backend_dir=backend_dir, feature_type=feature_type)
    
    def execute(self):
        pass