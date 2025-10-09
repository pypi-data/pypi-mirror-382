"""
@file shape.py
@brief Règle de filtrage par forme (dimensions et ratio) des bounding boxes.
"""

from .base import BaseRule

class ShapeRule(BaseRule):
    """
    @class ShapeRule
    @brief Applique un filtrage basé sur la taille et le ratio largeur/hauteur des objets.
    """
    def apply(self, bboxes, page_width, page_height):
        for box in bboxes:
            if box['label'] == self.params['label']:
                w, h = box['width']/page_width , box['height']/page_height          # taille relative à la taille de la page
                r = box['width'] / box['height'] if box['height'] != 0 else 0

                if  self.params['xmin'] <= w <= self.params['xmax'] or self.params['xmax'] == 0.0 :
                    if  self.params['ymin'] <= h <= self.params['ymax'] or self.params['ymax'] == 0.0 :
                        if self.params['rmin'] <= r <= self.params['rmax'] or self.params['rmax'] == 0.0 :
                            print(f"==> success on {box['label']} => {self.params['new_label']}.")
                            box['label'] = self.params['new_label']                            

        return bboxes
    
    