
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.io
import java.lang
import java.util
import jpype
import org.hipparchus
import org.orekit.bodies
import org.orekit.data
import org.orekit.frames
import org.orekit.gnss.metric.messages.ssr.subtype
import org.orekit.models.earth.ionosphere.nequick
import org.orekit.propagation
import org.orekit.time
import org.orekit.utils
import typing



class IonosphericDelayModel(org.orekit.utils.ParameterDriversProvider):
    """
    public interface IonosphericDelayModel extends :class:`~org.orekit.utils.ParameterDriversProvider`
    
        Defines a ionospheric model, used to calculate the path delay imposed to electro-magnetic signals between an orbital
        satellite and a ground station.
    
        Since 10.0, this interface can be used for models that aspire to estimate ionospheric parameters.
    
        Since:
            13.0.3
    """
    _pathDelay_1__T = typing.TypeVar('_pathDelay_1__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, absoluteDate: org.orekit.time.AbsoluteDate, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.AbsoluteDate`): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        """
        ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_1__T], topocentricFrame: org.orekit.frames.TopocentricFrame, fieldAbsoluteDate: org.orekit.time.FieldAbsoluteDate[_pathDelay_1__T], double: float, tArray: typing.Union[typing.List[_pathDelay_1__T], jpype.JArray]) -> _pathDelay_1__T:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.FieldAbsoluteDate`<T> receptionDate): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        
        """
        ...

class IonosphericMappingFunction:
    """
    public interface IonosphericMappingFunction
    
        Interface for mapping functions used in the ionospheric delay computation.
    
        The purpose of an ionospheric mapping function is to convert the Vertical Total Electron Content (VTEC) to a Slant Total
        Electron Content (STEC) using the following formula:
    
        .. code-block: java
        
         STEC = VTEC * m(e)
         
    
        With m(e) the ionospheric mapping function and e the satellite elevation.
    
        Since:
            10.2
    """
    _mappingFactor_1__T = typing.TypeVar('_mappingFactor_1__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def mappingFactor(self, double: float) -> float:
        """
            This method allows the computation of the ionospheric mapping factor.
        
            Parameters:
                elevation (double): the elevation of the satellite, in radians.
        
            Returns:
                the ionospheric mapping factor.
        
        """
        ...
    @typing.overload
    def mappingFactor(self, t: _mappingFactor_1__T) -> _mappingFactor_1__T:
        """
            This method allows the computation of the ionospheric mapping factor.
        
            Parameters:
                elevation (T): the elevation of the satellite, in radians.
        
            Returns:
                the ionospheric mapping factor.
        
        
        """
        ...

class IonosphericModel(org.orekit.utils.ParameterDriversProvider):
    """
    public interface IonosphericModel extends :class:`~org.orekit.utils.ParameterDriversProvider`
    
        Defines a ionospheric model, used to calculate the path delay imposed to electro-magnetic signals between an orbital
        satellite and a ground station.
    
        Since 10.0, this interface can be used for models that aspire to estimate ionospheric parameters.
    
        Since:
            7.1
    """
    _pathDelay_1__T = typing.TypeVar('_pathDelay_1__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        """
        ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_1__T], topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, tArray: typing.Union[typing.List[_pathDelay_1__T], jpype.JArray]) -> _pathDelay_1__T:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        
        """
        ...

class KlobucharIonoCoefficientsLoader(org.orekit.data.AbstractSelfFeedingLoader, org.orekit.data.DataLoader):
    """
    public class KlobucharIonoCoefficientsLoader extends :class:`~org.orekit.data.AbstractSelfFeedingLoader` implements :class:`~org.orekit.data.DataLoader`
    
        Loads Klobuchar-Style ionospheric coefficients a given input stream. A stream contains the alphas and betas coefficient
        for a given day.
    
        They are obtained from :class:`~org.orekit.models.earth.ionosphere.ftp:.ftp.aiub.unibe.ch.CODE`. Find more on the files
        at the `Astronomical Institute site
        <http://www.aiub.unibe.ch/research/code___analysis_center/klobuchar_style_ionospheric_coefficients/index_eng.html>`.
    
        The files are UNIX-style compressed (.Z) files. They have to be extracted to UTF-8 text files before being read by this
        loader.
    
        After extraction, it is assumed they are named CGIMDDD0.YYN where DDD and YY substitute day of year and 2-digits year.
    
        The format is always the same, with and example shown below. Only the last 2 lines contains the Klobuchar coefficients.
    
        Example:
    
        .. code-block: java
        
              2              NAVIGATION DATA     GPS                 RINEX VERSION / TYPE
         INXFIT V5.3         AIUB                06-JAN-17 09:12     PGM / RUN BY / DATE
         CODE'S KLOBUCHAR-STYLE IONOSPHERE MODEL FOR DAY 001, 2017   COMMENT
         Contact address: code(at)aiub.unibe.ch                      COMMENT
         Data archive:    ftp.unibe.ch/aiub/CODE/                    COMMENT
                          www.aiub.unibe.ch/download/CODE/           COMMENT
         WARNING: USE DATA AT SOUTHERN POLAR REGION WITH CARE        COMMENT
             1.2821D-08 -9.6222D-09 -3.5982D-07 -6.0901D-07          ION ALPHA
             1.0840D+05 -1.3197D+05 -2.6331D+05  4.0570D+05          ION BETA
                                                                     END OF HEADER
         
    
        It is not safe for multiple threads to share a single instance of this class.
    """
    DEFAULT_SUPPORTED_NAMES: typing.ClassVar[str] = ...
    """
    public static final :class:`~org.orekit.models.earth.ionosphere.https:.docs.oracle.com.javase.8.docs.api.java.lang.String?is` DEFAULT_SUPPORTED_NAMES
    
        Default supported files name pattern.
    
        Also see:
            :meth:`~constant`
    
    
    """
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, string: str): ...
    @typing.overload
    def __init__(self, string: str, dataProvidersManager: org.orekit.data.DataProvidersManager): ...
    def getAlpha(self) -> typing.MutableSequence[float]:
        """
            Returns the alpha coefficients array.
        
            Returns:
                the alpha coefficients array
        
        
        """
        ...
    def getBeta(self) -> typing.MutableSequence[float]:
        """
            Returns the beta coefficients array.
        
            Returns:
                the beta coefficients array
        
        
        """
        ...
    def getSupportedNames(self) -> str:
        """
            Description copied from class: :meth:`~org.orekit.data.AbstractSelfFeedingLoader.getSupportedNames`
            Get the supported names regular expression.
        
            Overrides:
                :meth:`~org.orekit.data.AbstractSelfFeedingLoader.getSupportedNames` in
                class :class:`~org.orekit.data.AbstractSelfFeedingLoader`
        
            Returns:
                the supported names.
        
            Also see:
                :meth:`~org.orekit.data.DataProvidersManager.feed`
        
        
        """
        ...
    def loadData(self, inputStream: java.io.InputStream, string: str) -> None: ...
    @typing.overload
    def loadKlobucharIonosphericCoefficients(self) -> None:
        """
            Load the data using supported names .
        """
        ...
    @typing.overload
    def loadKlobucharIonosphericCoefficients(self, dateComponents: org.orekit.time.DateComponents) -> None:
        """
            Load the data for a given day.
        
            Parameters:
                dateComponents (:class:`~org.orekit.time.DateComponents`): day given but its DateComponents
        
        
        """
        ...
    def stillAcceptsData(self) -> bool:
        """
            Check if the loader still accepts new data.
        
            This method is used to speed up data loading by interrupting crawling the data sets as soon as a loader has found the
            data it was waiting for. For loaders that can merge data from any number of sources (for example JPL ephemerides or
            Earth Orientation Parameters that are split among several files), this method should always return true to make sure no
            data is left over.
        
            Specified by:
                :meth:`~org.orekit.data.DataLoader.stillAcceptsData` in interface :class:`~org.orekit.data.DataLoader`
        
            Returns:
                true while the loader still accepts new data
        
        
        """
        ...

class EstimatedIonosphericModel(IonosphericModel, IonosphericDelayModel):
    """
    public class EstimatedIonosphericModel extends :class:`~org.orekit.models.earth.ionosphere.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`, :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
    
        An estimated ionospheric model. The ionospheric delay is computed according to the formula:
    
        40.3 δ = -------- * STEC with, STEC = VTEC * F(elevation) f²
        With:
    
          - f: The frequency of the signal in Hz.
          - STEC: The Slant Total Electron Content in TECUnits.
          - VTEC: The Vertical Total Electron Content in TECUnits.
          - F(elevation): A mapping function which depends on satellite elevation.
    
        The VTEC is estimated as a :class:`~org.orekit.utils.ParameterDriver`
    
        Since:
            10.2
    """
    VERTICAL_TOTAL_ELECTRON_CONTENT: typing.ClassVar[str] = ...
    """
    public static final :class:`~org.orekit.models.earth.ionosphere.https:.docs.oracle.com.javase.8.docs.api.java.lang.String?is` VERTICAL_TOTAL_ELECTRON_CONTENT
    
        Name of the parameter of this model: the Vertical Total Electron Content.
    
        Also see:
            :meth:`~constant`
    
    
    """
    def __init__(self, ionosphericMappingFunction: IonosphericMappingFunction, double: float): ...
    def getParametersDrivers(self) -> java.util.List[org.orekit.utils.ParameterDriver]: ...
    _pathDelay_3__T = typing.TypeVar('_pathDelay_3__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    _pathDelay_4__T = typing.TypeVar('_pathDelay_4__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    _pathDelay_5__T = typing.TypeVar('_pathDelay_5__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def pathDelay(self, double: float, double2: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.AbsoluteDate`): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            The path delay is computed for any elevation angle.
        
            Parameters:
                elevation (double): elevation of the satellite in radians
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters
        
            Returns:
                the path delay due to the ionosphere in m
        
        """
        ...
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float: ...
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, absoluteDate: org.orekit.time.AbsoluteDate, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float: ...
    @typing.overload
    def pathDelay(self, t: _pathDelay_3__T, double: float, tArray: typing.Union[typing.List[_pathDelay_3__T], jpype.JArray]) -> _pathDelay_3__T:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.FieldAbsoluteDate`<T> receptionDate): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            The path delay is computed for any elevation angle.
        
            Parameters:
                elevation (T): elevation of the satellite in radians
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        
        """
        ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_4__T], topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, tArray: typing.Union[typing.List[_pathDelay_4__T], jpype.JArray]) -> _pathDelay_4__T: ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_5__T], topocentricFrame: org.orekit.frames.TopocentricFrame, fieldAbsoluteDate: org.orekit.time.FieldAbsoluteDate[_pathDelay_5__T], double: float, tArray: typing.Union[typing.List[_pathDelay_5__T], jpype.JArray]) -> _pathDelay_5__T: ...

class GlobalIonosphereMapModel(IonosphericModel, IonosphericDelayModel):
    """
    public class GlobalIonosphereMapModel extends :class:`~org.orekit.models.earth.ionosphere.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`, :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
    
        Global Ionosphere Map (GIM) model. The ionospheric delay is computed according to the formulas:
    
        .. code-block: java
        
                   40.3
            δ =  --------  *  STEC      with, STEC = VTEC * F(elevation)
                    f²
         
        With:
    
          - f: The frequency of the signal in Hz.
          - STEC: The Slant Total Electron Content in TECUnits.
          - VTEC: The Vertical Total Electron Content in TECUnits.
          - F(elevation): A mapping function which depends on satellite elevation.
    
        The VTEC is read from a IONEX file. A file contains, for a given day, VTEC maps corresponding to snapshots at some
        sampling hours within the day. VTEC maps are TEC Values on regular latitude, longitude grids (typically global 2.5° x
        5.0° grids).
    
        A bilinear interpolation is performed the case of the user initialize the latitude and the longitude with values that
        are not contained in the stream.
    
        A temporal interpolation is also performed to compute the VTEC at the desired date.
    
        IONEX files are obtained from :class:`~org.orekit.models.earth.ionosphere.https:.cddis.nasa.gov.gnss.products.ionex`.
    
        The files have to be extracted to UTF-8 text files before being read by this loader.
    
        Example of file:
    
        .. code-block: java
        
              1.0            IONOSPHERE MAPS     GPS                 IONEX VERSION / TYPE
         BIMINX V5.3         AIUB                16-JAN-19 07:26     PGM / RUN BY / DATE
         BROADCAST IONOSPHERE MODEL FOR DAY 015, 2019                COMMENT
           2019     1    15     0     0     0                        EPOCH OF FIRST MAP
           2019     1    16     0     0     0                        EPOCH OF LAST MAP
           3600                                                      INTERVAL
             25                                                      # OF MAPS IN FILE
           NONE                                                      MAPPING FUNCTION
              0.0                                                    ELEVATION CUTOFF
                                                                     OBSERVABLES USED
           6371.0                                                    BASE RADIUS
              2                                                      MAP DIMENSION
            350.0 350.0   0.0                                        HGT1 / HGT2 / DHGT
             87.5 -87.5  -2.5                                        LAT1 / LAT2 / DLAT
           -180.0 180.0   5.0                                        LON1 / LON2 / DLON
             -1                                                      EXPONENT
         TEC/RMS values in 0.1 TECU; 9999, if no value available     COMMENT
                                                                     END OF HEADER
              1                                                      START OF TEC MAP
           2019     1    15     0     0     0                        EPOCH OF CURRENT MAP
             87.5-180.0 180.0   5.0 350.0                            LAT/LON1/LON2/DLON/H
            92   92   92   92   92   92   92   92   92   92   92   92   92   92   92   92
            92   92   92   92   92   92   92   92   92   92   92   92   92   92   92   92
            92   92   92   92   92   92   92   92   92   92   92   92   92   92   92   92
            92   92   92   92   92   92   92   92   92   92   92   92   92   92   92   92
            92   92   92   92   92   92   92   92   92
            ...
         
    
        Note that this model :meth:`~org.orekit.models.earth.ionosphere.GlobalIonosphereMapModel.pathDelay` methods *requires*
        the :class:`~org.orekit.frames.TopocentricFrame` to lie on a :class:`~org.orekit.bodies.OneAxisEllipsoid` body shape,
        because the single layer on which pierce point is computed must be an ellipsoidal shape at some altitude.
    
        Also see:
            "Schaer, S., W. Gurtner, and J. Feltens, 1998, IONEX: The IONosphere Map EXchange Format Version 1, February 25, 1998,
            Proceedings of the IGS AC Workshop Darmstadt, Germany, February 9–11, 1998"
    """
    @typing.overload
    def __init__(self, string: str): ...
    @typing.overload
    def __init__(self, string: str, dataProvidersManager: org.orekit.data.DataProvidersManager, timeScale: org.orekit.time.TimeScale): ...
    @typing.overload
    def __init__(self, string: str, dataProvidersManager: org.orekit.data.DataProvidersManager, timeScale: org.orekit.time.TimeScale, timeInterpolator: 'GlobalIonosphereMapModel.TimeInterpolator'): ...
    @typing.overload
    def __init__(self, timeScale: org.orekit.time.TimeScale, *dataSource: org.orekit.data.DataSource): ...
    @typing.overload
    def __init__(self, timeScale: org.orekit.time.TimeScale, timeInterpolator: 'GlobalIonosphereMapModel.TimeInterpolator', *dataSource: org.orekit.data.DataSource): ...
    def getInterpolator(self) -> 'GlobalIonosphereMapModel.TimeInterpolator':
        """
            Get the time interpolator used.
        
            Returns:
                time interpolator used
        
            Since:
                13.1.1
        
        
        """
        ...
    def getParametersDrivers(self) -> java.util.List[org.orekit.utils.ParameterDriver]: ...
    _pathDelay_2__T = typing.TypeVar('_pathDelay_2__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    _pathDelay_3__T = typing.TypeVar('_pathDelay_3__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float:
        """
            Description copied from interface: :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay`
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Description copied from interface: :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay`
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.AbsoluteDate`): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        """
        ...
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, absoluteDate: org.orekit.time.AbsoluteDate, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float: ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_2__T], topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, tArray: typing.Union[typing.List[_pathDelay_2__T], jpype.JArray]) -> _pathDelay_2__T:
        """
            Description copied from interface: :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay`
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Description copied from interface: :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay`
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.FieldAbsoluteDate`<T> receptionDate): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        
        """
        ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_3__T], topocentricFrame: org.orekit.frames.TopocentricFrame, fieldAbsoluteDate: org.orekit.time.FieldAbsoluteDate[_pathDelay_3__T], double: float, tArray: typing.Union[typing.List[_pathDelay_3__T], jpype.JArray]) -> _pathDelay_3__T: ...
    class TimeInterpolator(java.lang.Enum['GlobalIonosphereMapModel.TimeInterpolator']):
        NEAREST_MAP: typing.ClassVar['GlobalIonosphereMapModel.TimeInterpolator'] = ...
        SIMPLE_LINEAR: typing.ClassVar['GlobalIonosphereMapModel.TimeInterpolator'] = ...
        ROTATED_LINEAR: typing.ClassVar['GlobalIonosphereMapModel.TimeInterpolator'] = ...
        _valueOf_0__T = typing.TypeVar('_valueOf_0__T', bound=java.lang.Enum)  # <T>
        @typing.overload
        @staticmethod
        def valueOf(class_: typing.Type[_valueOf_0__T], string: str) -> _valueOf_0__T: ...
        @typing.overload
        @staticmethod
        def valueOf(string: str) -> 'GlobalIonosphereMapModel.TimeInterpolator': ...
        @staticmethod
        def values() -> typing.MutableSequence['GlobalIonosphereMapModel.TimeInterpolator']: ...

class KlobucharIonoModel(IonosphericModel, IonosphericDelayModel):
    """
    public class KlobucharIonoModel extends :class:`~org.orekit.models.earth.ionosphere.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`, :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
    
        Klobuchar ionospheric delay model. Klobuchar ionospheric delay model is designed as a GNSS correction model. The
        parameters for the model are provided by the GPS satellites in their broadcast messsage. This model is based on the
        assumption the electron content is concentrated in 350 km layer. The delay refers to L1 (1575.42 MHz). If the delay is
        sought for L2 (1227.60 MHz), multiply the result by 1.65 (Klobuchar, 1996). More generally, since ionospheric delay is
        inversely proportional to the square of the signal frequency f, to adapt this model to other GNSS frequencies f,
        multiply by (L1 / f)^2. References: ICD-GPS-200, Rev. C, (1997), pp. 125-128 Klobuchar, J.A., Ionospheric time-delay
        algorithm for single-frequency GPS users, IEEE Transactions on Aerospace and Electronic Systems, Vol. 23, No. 3, May
        1987 Klobuchar, J.A., "Ionospheric Effects on GPS", Global Positioning System: Theory and Applications, 1996,
        pp.513-514, Parkinson, Spilker.
    
        Since:
            7.1
    """
    @typing.overload
    def __init__(self, doubleArray: typing.Union[typing.List[float], jpype.JArray], doubleArray2: typing.Union[typing.List[float], jpype.JArray]): ...
    @typing.overload
    def __init__(self, doubleArray: typing.Union[typing.List[float], jpype.JArray], doubleArray2: typing.Union[typing.List[float], jpype.JArray], timeScale: org.orekit.time.TimeScale): ...
    def getParametersDrivers(self) -> java.util.List[org.orekit.utils.ParameterDriver]: ...
    _pathDelay_3__T = typing.TypeVar('_pathDelay_3__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    _pathDelay_4__T = typing.TypeVar('_pathDelay_4__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    _pathDelay_5__T = typing.TypeVar('_pathDelay_5__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            The path delay is computed for any elevation angle.
        
            Parameters:
                date (:class:`~org.orekit.time.AbsoluteDate`): current date
                geo (:class:`~org.orekit.bodies.GeodeticPoint`): geodetic point of receiver/station
                elevation (double): elevation of the satellite in radians
                azimuth (double): azimuth of the satellite in radians
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.AbsoluteDate`): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        """
        ...
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, absoluteDate: org.orekit.time.AbsoluteDate, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float: ...
    @typing.overload
    def pathDelay(self, absoluteDate: org.orekit.time.AbsoluteDate, geodeticPoint: org.orekit.bodies.GeodeticPoint, double: float, double2: float, double3: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float: ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_3__T], topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, tArray: typing.Union[typing.List[_pathDelay_3__T], jpype.JArray]) -> _pathDelay_3__T:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            The path delay is computed for any elevation angle.
        
            Parameters:
                date (:class:`~org.orekit.time.FieldAbsoluteDate`<T> date): current date
                geo (:class:`~org.orekit.bodies.FieldGeodeticPoint`<T> geo): geodetic point of receiver/station
                elevation (T): elevation of the satellite in radians
                azimuth (T): azimuth of the satellite in radians
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.FieldAbsoluteDate`<T> receptionDate): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        
        """
        ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_4__T], topocentricFrame: org.orekit.frames.TopocentricFrame, fieldAbsoluteDate: org.orekit.time.FieldAbsoluteDate[_pathDelay_4__T], double: float, tArray: typing.Union[typing.List[_pathDelay_4__T], jpype.JArray]) -> _pathDelay_4__T: ...
    @typing.overload
    def pathDelay(self, fieldAbsoluteDate: org.orekit.time.FieldAbsoluteDate[_pathDelay_5__T], fieldGeodeticPoint: org.orekit.bodies.FieldGeodeticPoint[_pathDelay_5__T], t: _pathDelay_5__T, t2: _pathDelay_5__T, double: float, tArray: typing.Union[typing.List[_pathDelay_5__T], jpype.JArray]) -> _pathDelay_5__T: ...

class SingleLayerModelMappingFunction(IonosphericMappingFunction):
    """
    public class SingleLayerModelMappingFunction extends :class:`~org.orekit.models.earth.ionosphere.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.models.earth.ionosphere.IonosphericMappingFunction`
    
        Single Layer Model (SLM) ionospheric mapping function.
    
        The SLM mapping function assumes a single ionospheric layer with a constant height for the computation of the mapping
        factor.
    
        Since:
            10.2
    
        Also see:
            "N. Ya’acob, M. Abdullah and M. Ismail, Determination of the GPS total electron content using single layer model (SLM)
            ionospheric mapping function, in International Journal of Computer Science and Network Security, vol. 8, no. 9, pp.
            154-160, 2008."
    """
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, double: float): ...
    _mappingFactor_1__T = typing.TypeVar('_mappingFactor_1__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def mappingFactor(self, double: float) -> float:
        """
            This method allows the computation of the ionospheric mapping factor.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericMappingFunction.mappingFactor` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericMappingFunction`
        
            Parameters:
                elevation (double): the elevation of the satellite, in radians.
        
            Returns:
                the ionospheric mapping factor.
        
        """
        ...
    @typing.overload
    def mappingFactor(self, t: _mappingFactor_1__T) -> _mappingFactor_1__T:
        """
            This method allows the computation of the ionospheric mapping factor.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericMappingFunction.mappingFactor` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericMappingFunction`
        
            Parameters:
                elevation (T): the elevation of the satellite, in radians.
        
            Returns:
                the ionospheric mapping factor.
        
        
        """
        ...

class SsrVtecIonosphericModel(IonosphericModel, IonosphericDelayModel):
    """
    public class SsrVtecIonosphericModel extends :class:`~org.orekit.models.earth.ionosphere.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`, :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
    
        Ionospheric model based on SSR IM201 message.
    
        Within this message, the ionospheric VTEC is provided using spherical harmonic expansions. For a given ionospheric
        layer, the slant TEC value is calculated using the satellite elevation and the height of the corresponding layer. The
        total slant TEC is computed by the sum of the individual slant TEC for each layer.
    
        Since:
            11.0
    
        Also see:
            "IGS State Space Representation (SSR) Format, Version 1.00, October 2020."
    """
    def __init__(self, ssrIm201: org.orekit.gnss.metric.messages.ssr.subtype.SsrIm201): ...
    def getParametersDrivers(self) -> java.util.List[org.orekit.utils.ParameterDriver]: ...
    _pathDelay_2__T = typing.TypeVar('_pathDelay_2__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    _pathDelay_3__T = typing.TypeVar('_pathDelay_3__T', bound=org.hipparchus.CalculusFieldElement)  # <T>
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.SpacecraftState`): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.AbsoluteDate`): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (double[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        """
        ...
    @typing.overload
    def pathDelay(self, spacecraftState: org.orekit.propagation.SpacecraftState, topocentricFrame: org.orekit.frames.TopocentricFrame, absoluteDate: org.orekit.time.AbsoluteDate, double: float, doubleArray: typing.Union[typing.List[float], jpype.JArray]) -> float: ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_2__T], topocentricFrame: org.orekit.frames.TopocentricFrame, double: float, tArray: typing.Union[typing.List[_pathDelay_2__T], jpype.JArray]) -> _pathDelay_2__T:
        """
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
            Calculates the ionospheric path delay for the signal path from a ground station to a satellite.
        
            This method is intended to be used for orbit determination issues. In that respect, if the elevation is below 0° the
            path delay will be equal to zero.
        
            For individual use of the ionospheric model (i.e. not for orbit determination), another method signature can be
            implemented to compute the path delay for any elevation angle.
        
            Specified by:
                :meth:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel.pathDelay` in
                interface :class:`~org.orekit.models.earth.ionosphere.IonosphericDelayModel`
        
            Parameters:
                state (:class:`~org.orekit.propagation.FieldSpacecraftState`<T> state): spacecraft state
                baseFrame (:class:`~org.orekit.frames.TopocentricFrame`): base frame associated with the station
                receptionDate (:class:`~org.orekit.time.FieldAbsoluteDate`<T> receptionDate): date at signal reception
                frequency (double): frequency of the signal in Hz
                parameters (T[]): ionospheric model parameters at state date
        
            Returns:
                the path delay due to the ionosphere in m
        
        
        """
        ...
    @typing.overload
    def pathDelay(self, fieldSpacecraftState: org.orekit.propagation.FieldSpacecraftState[_pathDelay_3__T], topocentricFrame: org.orekit.frames.TopocentricFrame, fieldAbsoluteDate: org.orekit.time.FieldAbsoluteDate[_pathDelay_3__T], double: float, tArray: typing.Union[typing.List[_pathDelay_3__T], jpype.JArray]) -> _pathDelay_3__T: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("org.orekit.models.earth.ionosphere")``.

    EstimatedIonosphericModel: typing.Type[EstimatedIonosphericModel]
    GlobalIonosphereMapModel: typing.Type[GlobalIonosphereMapModel]
    IonosphericDelayModel: typing.Type[IonosphericDelayModel]
    IonosphericMappingFunction: typing.Type[IonosphericMappingFunction]
    IonosphericModel: typing.Type[IonosphericModel]
    KlobucharIonoCoefficientsLoader: typing.Type[KlobucharIonoCoefficientsLoader]
    KlobucharIonoModel: typing.Type[KlobucharIonoModel]
    SingleLayerModelMappingFunction: typing.Type[SingleLayerModelMappingFunction]
    SsrVtecIonosphericModel: typing.Type[SsrVtecIonosphericModel]
    nequick: org.orekit.models.earth.ionosphere.nequick.__module_protocol__
