from .position import PositionRule
from .shape import ShapeRule
from .proximity import ProximityRule
from .merge import MergeRule
from .delete import DeleteRule
from .info import InfoRule
from .detection import DetectionRule

RULE_CLASSES = {
    'info': InfoRule,
    'detection': DetectionRule,
    'position': PositionRule,
    'shape': ShapeRule,
    'proximity': ProximityRule,
    'merge': MergeRule,
    'delete': DeleteRule,
}