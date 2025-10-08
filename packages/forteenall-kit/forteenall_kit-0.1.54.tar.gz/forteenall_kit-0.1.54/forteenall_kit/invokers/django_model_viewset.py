from ..feature import KitFeature



class SerializerFeatureData:
    
    pass

class Feature(KitFeature):
    
    def __init__(self):
        feature_type = 'django_model_viewset'
        super().__init__(feature_type=feature_type)
    
    def execute(self):
        pass