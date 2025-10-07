
from .rtdetr_apache_base import RTDETRApacheBase

__all__ = [
    'MegaDetectorV6Apache'
]

class MegaDetectorV6Apache(RTDETRApacheBase):
    """
    MegaDetectorV6 is a specialized class derived from the RTDETRApacheBase class 
    that is specifically designed for detecting animals, persons, and vehicles.
    
    Attributes:
        CLASS_NAMES (dict): Mapping of class IDs to their respective names.
    """
    
    CLASS_NAMES = {
        0: "animal",
        1: "person",
        2: "vehicle"
    }

    def __init__(self, weights=None, device="cpu", pretrained=True, version='MDV6-rtdetr-x-apache'):
        """
        Initializes the MegaDetectorV6 model with the option to load pretrained weights.
        
        Args:
            weights (str, optional): Path to the weights file.
            device (str, optional): Device to load the model on (e.g., "cpu" or "cuda"). Default is "cpu".
            pretrained (bool, optional): Whether to load the pretrained model. Default is True.
            version (str, optional): Version of the model to load. Default is 'MDV6-rtdetr-x-apache'.
        """
        self.IMAGE_SIZE = 640

        if version == "MDV6-apa-rtdetr-c":
            url = "https://zenodo.org/records/15398270/files/MDV6-apa-rtdetr-c.pth?download=1"
            self.MODEL_NAME = "MDV6-apa-rtdetr-c.pth"
        elif version == "MDV6-apa-rtdetr-e":
            url = "https://zenodo.org/records/15398270/files/MDV6-apa-rtdetr-e.pth?download=1"
            self.MODEL_NAME = "MDV6-apa-rtdetr-e.pth"
        else:
            raise ValueError('Select a valid model version: MDV6-apa-rtdetr-c or MDV6-apa-rtdetr-e')

        super(MegaDetectorV6Apache, self).__init__(weights=weights, device=device, url=url)