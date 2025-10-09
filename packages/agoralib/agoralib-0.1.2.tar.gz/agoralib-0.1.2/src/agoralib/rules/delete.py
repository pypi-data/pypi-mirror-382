"""
@file delete.py
@brief Règle pour supprimer des objets selon leur label.
"""

from .base import BaseRule


class DeleteRule(BaseRule):
    """
    @class DeleteRule
    @brief Supprime les objets correspondant à un label donné.
    """     
    def apply(self, bboxes, page_width, page_height):
        # New empty list
        filtered_bboxes = []
        for box in bboxes:
            if box['label'] == self.params['label'] and box['label'] != "page":
                print(f"==> success on {box['label']} : DELETED")
                # Box a ne pas ajouter ==> deleted
            else:
                # BB page ne peut pas etre DELETED
                filtered_bboxes.append(box)
    
        return filtered_bboxes