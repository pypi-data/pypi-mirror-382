"""
@file merge.py
@brief Règle de fusion entre deux objets proches pour créer une entité composite.
"""
from cProfile import label
import copy
from .base import BaseRule
from agoralib.rules.utils import merge_compatibilty


class MergeRule(BaseRule):
    """
    @class MergeRule
    @brief Fusionne dees EoC selon des conditions de proximité.
    """

    
    def merge_bounding_boxes_with_children(self, bboxes, x_thresh, y_thresh, max_dist_x, max_dist_y):
        """
        Fusionne plusieurs bounding boxes en une seule contenant tous les enfants,
        si elles sont suffisamment proches ou se recouvrent.

        Args:
            bboxes (list of dict): BB avec 'x', 'y', 'width', 'height', 'label'
            x_thresh, y_thresh (float): Seuils de recouvrement
            max_dist_x, max_dist_y (float): Distances maximales pour fusionner

        Returns:
            dict or None: BB fusionnée avec children, ou None si fusion impossible
        """
        if not bboxes:
            return None

        # On reteste la compatibilité des BB du cluster ?
        firstbb = bboxes[0].copy()
        merged = [bboxes[0]]
        remaining = bboxes[1:]

        i = 0
        while i < len(remaining):
            bb = remaining[i]
            if any(merge_compatibilty(bb, m, x_thresh, y_thresh, max_dist_x, max_dist_y) for m in merged):
                merged.append(remaining.pop(i))
                i = 0
            else:
                i += 1

        # Si cluster pas homogene  :
        if len(merged) < len(bboxes):
            return None
        
        # Si cluster homogene :
        x_min = min(bb["x"] for bb in merged)
        y_min = min(bb["y"] for bb in merged)
        x_max = max(bb["x"] + bb["width"] for bb in merged)
        y_max = max(bb["y"] + bb["height"] for bb in merged)        
        for i, bb in enumerate(merged):
            bb['id'] = f"{firstbb['id']}_{i}" 
            bb['parent'] = f"{firstbb['id']}"                     

        return {
            "x": x_min,
            "y": y_min,
            "width": x_max - x_min,
            "height": y_max - y_min,
            "label": self.params['new_label'],
            "id": firstbb['id'],
            "parent": firstbb['parent'],
            "children": merged,
        }


    def apply(self, bboxes, page_width, page_height):
        """
        Regroupe automatiquement des bounding boxes compatibles en clusters,
        puis les fusionne avec enfants.

        Args    :
            bboxes (list of dict): Liste de BB avec 'x', 'y', 'width', 'height', 'label'
            image size (not used here)
        Returns:
            list of BB finales (fusionnées ou non)
        """

        # x_thresh (xmin) , y_thresh (ymin) : Seuils de recouvrement  (float)        
        x_thresh = self.params['xmin'] ; y_thresh = self.params['ymin']
        # max_dist_x (xmax) , max_dist_y (ymax) : Distances pour fusion (float)
        max_dist_x = self.params['xmax'] ; max_dist_y = self.params['ymax']

        clusters = []
        unprocessed = bboxes[:]
        
        while unprocessed:
            bb = unprocessed.pop(0)
            if bb['label'] == self.params['label'] :
                cluster = [bb]
                i = 0

                # boucle recherche des BB simialires à bb
                while i < len(unprocessed):
                    other = unprocessed[i]    
                    compatible = False
                    for m in cluster:
                        if other['label'] == self.params['neighbor_label'] and merge_compatibilty(other, m, x_thresh, y_thresh, max_dist_x, max_dist_y):
                            compatible = True
                            break
                    if compatible:
                        cluster.append(unprocessed.pop(i))
                        i = 0
                    else:
                        i += 1
    
                # test si cluster contient plus de 1 BB
                if len(cluster) > 1:
                    # Ajout du cluster créé avec children ==> a flatteniser 
                    merged = self.merge_bounding_boxes_with_children(cluster, x_thresh, y_thresh, max_dist_x, max_dist_y)
                    print(f"==> success on {bb['label']} => {self.params['new_label']}.")
                    
                    clusters.append(merged)
                    #Flatten children
                    for bbx in merged['children']:
                        bbx['label'] = self.params['new_label'] + "_" + bbx['label']
                        clusters.append(bbx)
                    merged['children'] = []
                    
                else:
                    # 1 seule BB
                    clusters.append(bb)
            else:
                clusters.append(bb)
            
        return clusters