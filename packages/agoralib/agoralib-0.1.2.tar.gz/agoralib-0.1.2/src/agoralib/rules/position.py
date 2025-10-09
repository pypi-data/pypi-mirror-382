"""
@file position.py
@brief Règle de filtrage par position des bounding boxes.
"""

from .base import BaseRule


class PositionRule(BaseRule):
    """
    @class PositionRule
    @brief Applique un filtrage basé sur les coordonnées x/y des objets.
    """
    def apply(self, bboxes, page_width, page_height): 
        for box in bboxes:
            if box['label'] == self.params['label']:
                x, y = (box['x'] + box['width']/2)/page_width , (box['y'] + box['height']/2)/page_height    # x,y = centre de gravite BB en % de taille d image
                if self.params['xmin'] <= x <= self.params['xmax'] or self.params['xmax'] == 0.0:
                    if self.params['ymin'] <= y <= self.params['ymax'] or self.params['ymax'] == 0.0:
                        print(f"==> success on {box['label']} => {self.params['new_label']}.")
                        box['label'] = self.params['new_label']
                        
        return bboxes
    