
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.io
import org.orekit.models.earth
import typing



class AtmosphericRefractionModel(java.io.Serializable):
    """
    public interface AtmosphericRefractionModel extends :class:`~org.orekit.models.https:.docs.oracle.com.javase.8.docs.api.java.io.Serializable?is`
    
        Defines an refraction model that can be used to correct for the apparent position of an object due to atmospheric
        effects.
    
        Since:
            6.1
    """
    def getRefraction(self, double: float) -> float:
        """
            Compute the refraction angle from the true (geometrical) elevation.
        
            Parameters:
                trueElevation (double): true elevation (rad)
        
            Returns:
                refraction angle (rad)
        
        
        """
        ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("org.orekit.models")``.

    AtmosphericRefractionModel: typing.Type[AtmosphericRefractionModel]
    earth: org.orekit.models.earth.__module_protocol__
