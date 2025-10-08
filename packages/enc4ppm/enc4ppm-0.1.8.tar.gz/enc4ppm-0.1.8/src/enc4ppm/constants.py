from enum import Enum

class LabelingType(Enum):
    NEXT_ACTIVITY = 'next_activity'
    REMAINING_TIME = 'remaining_time'
    REMAINING_TIME_CLASSIFICATION = 'remaining_time_classification'
    OUTCOME = 'outcome'
    CUSTOM = 'custom'
    NONE = 'none'


class CategoricalEncoding(Enum):
    STRING = 'string'
    ONE_HOT = 'one_hot'


class NumericalScaling(Enum):
    NONE = 'none'
    STANDARDIZATION = 'standardization'


class PrefixStrategy(Enum):
    UP_TO_SPECIFIED = 'up_to_specified'
    ONLY_SPECIFIED = 'only_specified'