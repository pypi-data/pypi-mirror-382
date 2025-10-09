"""
@file detection.py
@brief Règle pour detecter des CC normalement jamais utilisée avec Arkindex (NOT CHECKED).
"""

from .base import BaseRule

import cv2
import numpy as np
import requests

class DetectionRule(BaseRule):
    """
    @class DetectionRule
    @brief Extract connected components from a IIIF image using binarisation.
           Requires one input bbox with a label and a IIIF URL.
    """

    def apply(self, bboxes, page_width, page_height):
    
        # check bboxes validity
        if not isinstance(bboxes, list) or len(bboxes) == 0:
            print("==> Error: 'bboxes' is empty or not a list.")
            return []

        box = bboxes[0]
        if not isinstance(box, dict):
            print("==> Error: First element in 'bboxes' is not a dictionary.")
            return []

        required_keys = ["label", "URL"]
        for key in required_keys:
            if key not in box:
                print(f"==> Error: Missing key '{key}' in the bounding box.")
                return []

        #check rule parameters
        page_label = self.params.get("label", None)
        new_label = self.params.get("new_label", None)
        threshold = int(self.params.get("threshold", None))
        areamin = float(self.params.get("areamin", None))
        
        if page_label is None or new_label is None or threshold is None or areamin is None:
            print("==> Error: somethings missing in rule parameters.")
            return []

        #check rule vs bboxes
        if box["label"] != page_label or not box["URL"]:
            print("==> Error: label or URL mismatch.")
            return []


        # Everythings ready for binarisation        
        img_url = box["URL"]
        print(f"==> Fetching IIIF image from {img_url}...")

        try:
            response = requests.get(img_url)
            response.raise_for_status()
            image_bytes = np.asarray(bytearray(response.content), dtype=np.uint8)
            img = cv2.imdecode(image_bytes, cv2.IMREAD_GRAYSCALE)  # chargement en niveau de gris
            if img is None:
                raise ValueError("OpenCV failed to decode image.")
        except Exception as e:
            print(f"==> Error: Unable to load image from URL: {e}")
            return []

        # Binarisation 
        if threshold == 0:
            print("==> threshold = 0 => otsu")
            _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            print("==> Binarisation => threshold = ",threshold)            
            _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)            

        # Inversion (optionnel ? a verifier ?)
        binary = 255 - binary
        
        debug_path = "./log/img.png"
        cv2.imwrite(debug_path, img)
        debug_path = "./log/binarized.png"
        cv2.imwrite(debug_path, binary)
        print(f"==> Img/Binarized image saved to: {debug_path}")

        # Composantes connexes
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary)

        components = []
        components.append(box) #ajout BB page entiere
        
        # Copie couleur de l'image pour dessiner les bounding boxes
        if len(img.shape) == 2:
            out_img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            out_img = img.copy()		        
        
        print("==> Min ratio area to be added = ",areamin)   
        cpt = 0
        for i in range(1, num_labels):  # 0 est l'arrière-plan
            x, y, w, h, area = stats[i]
            
            # test inclusion : le rect i est contenu dans le rect j
            inside = False
            #for j in range(1, num_labels):  
            #    x2, y2, w2, h2, area2 = stats[j]
            #    if i != j:                    
            #        if (x >= x2 and y >= y2 and
            #            x + w <= x2 + w2 and
            #            y + h <= y2 + h2):
            #            inside = True
            #            break

            if inside or float(area)/float(page_height*page_width) < areamin :
                continue  # ignore petites composantes

            cpt = cpt + 1    
            components.append({
                "id" : f"0_{cpt}",       # CC sont children de page 
                "parent" : "0",        # CC sont children de page 
                "label": new_label,
                "x": int(x),
                "y": int(y),
                "width": int(w),
                "height": int(h),                
            })
            # Dessiner la bounding box
            cv2.rectangle(out_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                            
		# Sauvegarde de l'image avec bounding boxes
        debug_path = "./log/components.png"
        cv2.imwrite(debug_path, out_img)
        print(f"==> Image with connected components saved to: {debug_path}")

        print(f"==> Detected {len(components)} connected components.")

        return components
