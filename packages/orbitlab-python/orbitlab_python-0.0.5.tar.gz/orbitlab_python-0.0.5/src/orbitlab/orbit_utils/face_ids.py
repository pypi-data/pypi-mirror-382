from enum import Enum

class FaceId(Enum):
    """Enum for predefined face IDs.
    
    Attributes:
        BRINKING (int): Face ID for "BRINKING".
        BREATHE (int): Face ID for "BREATHE".
        COMPASSION (int): Face ID for "COMPASSION".
        CURIOUS (int): Face ID for "CURIOUS".
        ERROR (int): Face ID for "ERROR".
        HEART_EYES (int): Face ID for "HEART_EYES".
        HELLO (int): Face ID for "HELLO".
        LOADING (int): Face ID for "LOADING".
        PLAYFUL (int): Face ID for "PLAYFUL".
        SHY (int): Face ID for "SHY".
        STAR_EYES (int): Face ID for "STAR_EYES".
        SURPRISED (int): Face ID for "SURPRISED".
        THANK_YOU (int): Face ID for "THANK_YOU".
    """
    BRINKING = 0
    BREATHE = 1
    COMPASSION = 2
    CURIOUS = 3
    ERROR = 4
    HEART_EYES = 5
    HELLO = 6
    LOADING = 7
    PLAYFUL = 8
    SHY = 9
    STAR_EYES = 10
    SURPRISED = 11
    THANK_YOU = 12