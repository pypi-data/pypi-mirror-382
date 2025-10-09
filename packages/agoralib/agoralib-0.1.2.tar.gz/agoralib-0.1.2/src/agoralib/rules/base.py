"""
@file base.py
@brief Définition de la classe de base pour toutes les règles de filtrage.
"""

class BaseRule:
    """
    @class BaseRule
    @brief Classe abstraite pour toutes les règles de filtrage.
    """
    def __init__(self, params):
        self.params = params
    
    def apply(self, bboxes, page_width, page_height):
        """
        @brief Méthode abstraite pour appliquer une règle sur une liste de bounding boxes.
        @param bboxes Liste des bounding boxes à traiter.
        @param page_width taille de l image.
        @param page_height taille de l image.
        @return Liste modifiée après application de la règle.
        """
        raise NotImplementedError("Chaque règle doit implémenter apply()")