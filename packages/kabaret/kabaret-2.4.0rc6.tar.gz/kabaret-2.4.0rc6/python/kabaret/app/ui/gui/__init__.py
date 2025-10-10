

from . import styles                        # init the style manager
from .styles import neonative, dark, gray

neonative.NeonativeStyle()  # registers the style in the StyleManager
gray.GrayStyle()            # # registers the style in the StyleManager
dark.DarkStyle()            # registers the style in the StyleManager, last one is default one.


from .standalone import KabaretStandaloneGUISession
from .embedded import KabaretEmbeddedGUISession
