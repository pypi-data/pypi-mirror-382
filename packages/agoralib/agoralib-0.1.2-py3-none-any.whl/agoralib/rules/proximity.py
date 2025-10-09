"""
@file proximity.py
@brief Règle de reclassification basée sur la proximité d’autres objets.
"""

from .base import BaseRule
from agoralib.rules.utils import bbox_overlap_metrics

class ProximityRule(BaseRule):
    """
    @class ProximityRule
    @brief Change le label d un objet en fonction de la proximité avec un autre label donné.
    """
    def apply(self, bboxes, page_width, page_height):
        for box in bboxes:
            if box['label'] == self.params['label']:
                for other in bboxes:
                    if other['label'] == self.params['neighbor_label']:
                        dxright = abs(other['x'] - (box['x'] + box['width']))
                        dxright = dxright/box['width']
                        dxleft = abs(box['x'] - (other['x'] + other['width']))
                        dxleft = dxleft/box['width']
                        dybottom = abs(other['y'] - (box['y'] + box['height']))
                        dybottom = dybottom / box['height']
                        dytop = abs(box['y'] - (other['y'] + other['height']))
                        dytop = dytop / box['height']
                        m = bbox_overlap_metrics(box, other)                                                

                        if ( (dxleft <= self.params['xmin'] or dxright <= self.params['xmax']) and m["x_overlap_ratio"] >= 0.25 ) or ( (dytop <= self.params['ymin'] or dybottom <= self.params['ymax']) and m["y_overlap_ratio"] >= 0.25 ) :
                            print(f"==> success on {box['label']} => {self.params['new_label']}.")
                            box['label'] = self.params['new_label']
        return bboxes
    