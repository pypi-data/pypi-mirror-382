
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import java.util
import java.util.function
import jpype
import org.hipparchus.random
import org.orekit.estimation.measurements
import org.orekit.estimation.measurements.gnss
import org.orekit.frames
import org.orekit.propagation
import org.orekit.propagation.events
import org.orekit.propagation.sampling
import org.orekit.time
import typing



class GeneratedMeasurementSubscriber:
    """
    public interface GeneratedMeasurementSubscriber
    
        Interface for subscribing to generated :class:`~org.orekit.estimation.measurements.EstimatedMeasurementBase` events.
    
        Since:
            12.0
    """
    def handleGeneratedMeasurement(self, estimatedMeasurementBase: org.orekit.estimation.measurements.EstimatedMeasurementBase[typing.Any]) -> None:
        """
            Handle a generated measurement.
        
            Parameters:
                measurement (:class:`~org.orekit.estimation.measurements.EstimatedMeasurementBase`<?> measurement): measurements that has just been generated
        
        
        """
        ...
    def init(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Initialize subscriber at the start of a measurements generation.
        
            This method is called once at the start of the measurements generation. It may be used by the subscriber to initialize
            some internal data if needed.
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...

class Generator:
    """
    public class Generator extends :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is`
    
        Main generator for :class:`~org.orekit.estimation.measurements.ObservedMeasurement`.
    
        Since:
            9.3
    """
    def __init__(self): ...
    @typing.overload
    def addPropagator(self, propagator: org.orekit.propagation.Propagator) -> org.orekit.estimation.measurements.ObservableSatellite:
        """
            Add a propagator.
        
            Parameters:
                propagator (:class:`~org.orekit.propagation.Propagator`): to add
        
            Returns:
                satellite satellite propagated by the propagator
        
            Add a propagator.
        
            Parameters:
                propagator (:class:`~org.orekit.propagation.Propagator`): to add
                name (:class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.String?is`): satellite name (if null, a default name built from index will be used)
        
            Returns:
                satellite satellite propagated by the propagator
        
            Since:
                13.0
        
        
        """
        ...
    @typing.overload
    def addPropagator(self, propagator: org.orekit.propagation.Propagator, string: str) -> org.orekit.estimation.measurements.ObservableSatellite: ...
    _addScheduler__T = typing.TypeVar('_addScheduler__T', bound=org.orekit.estimation.measurements.ObservedMeasurement)  # <T>
    def addScheduler(self, scheduler: 'Scheduler'[_addScheduler__T]) -> None:
        """
            Add a sequences generator for a specific measurement type.
        
            Parameters:
                scheduler (:class:`~org.orekit.estimation.measurements.generation.Scheduler`<T> scheduler): sequences generator to add
        
        
        """
        ...
    def addSubscriber(self, generatedMeasurementSubscriber: GeneratedMeasurementSubscriber) -> None:
        """
            Add a subscriber.
        
            Parameters:
                subscriber (:class:`~org.orekit.estimation.measurements.generation.GeneratedMeasurementSubscriber`): to add
        
            Since:
                12.0
        
            Also see:
                :class:`~org.orekit.estimation.measurements.generation.GatheringSubscriber`
        
        
        """
        ...
    def generate(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Generate measurements.
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...
    def getPropagator(self, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite) -> org.orekit.propagation.Propagator:
        """
            Get a registered propagator.
        
            Parameters:
                satellite (:class:`~org.orekit.estimation.measurements.ObservableSatellite`): satellite propagated by the propagator :meth:`~org.orekit.estimation.measurements.generation.Generator.addPropagator`
        
            Returns:
                propagator corresponding to satellite
        
        
        """
        ...

_MeasurementBuilder__T = typing.TypeVar('_MeasurementBuilder__T', bound=org.orekit.estimation.measurements.ObservedMeasurement)  # <T>
class MeasurementBuilder(typing.Generic[_MeasurementBuilder__T]):
    """
    public interface MeasurementBuilder<T extends :class:`~org.orekit.estimation.measurements.ObservedMeasurement`<T>>
    
        Interface for generating individual :class:`~org.orekit.estimation.measurements.ObservedMeasurement`.
    
        Since:
            9.3
    """
    def addModifier(self, estimationModifier: org.orekit.estimation.measurements.EstimationModifier[_MeasurementBuilder__T]) -> None: ...
    @typing.overload
    def build(self, absoluteDate: org.orekit.time.AbsoluteDate, map: typing.Union[java.util.Map[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator], typing.Mapping[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator]]) -> org.orekit.estimation.measurements.EstimatedMeasurementBase[_MeasurementBuilder__T]: ...
    @typing.overload
    def build(self, absoluteDate: org.orekit.time.AbsoluteDate, spacecraftStateArray: typing.Union[typing.List[org.orekit.propagation.SpacecraftState], jpype.JArray]) -> org.orekit.estimation.measurements.EstimatedMeasurementBase[_MeasurementBuilder__T]: ...
    def getModifiers(self) -> java.util.List[org.orekit.estimation.measurements.EstimationModifier[_MeasurementBuilder__T]]: ...
    def getSatellites(self) -> typing.MutableSequence[org.orekit.estimation.measurements.ObservableSatellite]:
        """
            Get the satellites related to this measurement.
        
            Returns:
                satellites related to this measurement
        
            Since:
                12.0
        
        
        """
        ...
    def init(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Initialize builder at the start of a measurements generation.
        
            This method is called once at the start of the measurements generation. It may be used by the builder to initialize some
            internal data if needed, typically setting up parameters reference dates.
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...

_Scheduler__T = typing.TypeVar('_Scheduler__T', bound=org.orekit.estimation.measurements.ObservedMeasurement)  # <T>
class Scheduler(typing.Generic[_Scheduler__T]):
    """
    public interface Scheduler<T extends :class:`~org.orekit.estimation.measurements.ObservedMeasurement`<T>>
    
        Interface for generating :class:`~org.orekit.estimation.measurements.ObservedMeasurement` sequences.
    
        Since:
            9.3
    """
    def generate(self, map: typing.Union[java.util.Map[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator], typing.Mapping[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator]]) -> java.util.SortedSet[org.orekit.estimation.measurements.EstimatedMeasurementBase[_Scheduler__T]]: ...
    def getBuilder(self) -> MeasurementBuilder[_Scheduler__T]: ...
    def init(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Initialize scheduler at the start of a measurements generation.
        
            This method is called once at the start of the measurements generation. It may be used by the scheduler to initialize
            some internal data if needed, typically :meth:`~org.orekit.estimation.measurements.generation.MeasurementBuilder.init`.
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...

class SignSemantic(java.lang.Enum['SignSemantic']):
    """
    public enum SignSemantic extends :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.Enum?is`<:class:`~org.orekit.estimation.measurements.generation.SignSemantic`>
    
        Enumerate for the semantic of the :code:`g` function sign during measurements generation.
    
        Since:
            9.3
    
        Also see:
            :class:`~org.orekit.estimation.measurements.generation.EventBasedScheduler`
    """
    FEASIBLE_MEASUREMENT_WHEN_POSITIVE: typing.ClassVar['SignSemantic'] = ...
    FEASIBLE_MEASUREMENT_WHEN_NEGATIVE: typing.ClassVar['SignSemantic'] = ...
    def measurementIsFeasible(self, double: float) -> bool:
        """
            Check if measurement is feasible.
        
            Parameters:
                g (double): value of the detector g function
        
            Returns:
                true if measurement is feasible
        
        
        """
        ...
    _valueOf_0__T = typing.TypeVar('_valueOf_0__T', bound=java.lang.Enum)  # <T>
    @typing.overload
    @staticmethod
    def valueOf(class_: typing.Type[_valueOf_0__T], string: str) -> _valueOf_0__T: ...
    @typing.overload
    @staticmethod
    def valueOf(string: str) -> 'SignSemantic':
        """
            Returns the enum constant of this type with the specified name. The string must match *exactly* an identifier used to
            declare an enum constant in this type. (Extraneous whitespace characters are not permitted.)
        
            Parameters:
                name (:class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.String?is`): the name of the enum constant to be returned.
        
            Returns:
                the enum constant with the specified name
        
            Raises:
                :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.IllegalArgumentException?is`: if this enum type has no constant with the specified name
                :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.NullPointerException?is`: if the argument is null
        
        
        """
        ...
    @staticmethod
    def values() -> typing.MutableSequence['SignSemantic']:
        """
            Returns an array containing the constants of this enum type, in the order they are declared. This method may be used to
            iterate over the constants as follows:
        
            .. code-block: java
            
            for (SignSemantic c : SignSemantic.values())
                System.out.println(c);
            
        
            Returns:
                an array containing the constants of this enum type, in the order they are declared
        
        
        """
        ...

_AbstractMeasurementBuilder__T = typing.TypeVar('_AbstractMeasurementBuilder__T', bound=org.orekit.estimation.measurements.ObservedMeasurement)  # <T>
class AbstractMeasurementBuilder(MeasurementBuilder[_AbstractMeasurementBuilder__T], typing.Generic[_AbstractMeasurementBuilder__T]):
    """
    public abstract class AbstractMeasurementBuilder<T extends :class:`~org.orekit.estimation.measurements.ObservedMeasurement`<T>> extends :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.estimation.measurements.generation.MeasurementBuilder`<T>
    
        Base class for :class:`~org.orekit.estimation.measurements.generation.MeasurementBuilder`.
    
        Since:
            9.3
    """
    def addModifier(self, estimationModifier: org.orekit.estimation.measurements.EstimationModifier[_AbstractMeasurementBuilder__T]) -> None: ...
    @typing.overload
    def build(self, absoluteDate: org.orekit.time.AbsoluteDate, spacecraftStateArray: typing.Union[typing.List[org.orekit.propagation.SpacecraftState], jpype.JArray]) -> org.orekit.estimation.measurements.EstimatedMeasurementBase[_AbstractMeasurementBuilder__T]: ...
    @typing.overload
    def build(self, absoluteDate: org.orekit.time.AbsoluteDate, map: typing.Union[java.util.Map[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator], typing.Mapping[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator]]) -> org.orekit.estimation.measurements.EstimatedMeasurementBase[_AbstractMeasurementBuilder__T]: ...
    def getModifiers(self) -> java.util.List[org.orekit.estimation.measurements.EstimationModifier[_AbstractMeasurementBuilder__T]]: ...
    def getSatellites(self) -> typing.MutableSequence[org.orekit.estimation.measurements.ObservableSatellite]:
        """
            Get the satellites related to this measurement.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.MeasurementBuilder.getSatellites` in
                interface :class:`~org.orekit.estimation.measurements.generation.MeasurementBuilder`
        
            Returns:
                satellites related to this measurement
        
        
        """
        ...
    def init(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Initialize builder at the start of a measurements generation.
        
            This method is called once at the start of the measurements generation. It may be used by the builder to initialize some
            internal data if needed, typically setting up parameters reference dates.
        
            This implementation stores the time span of the measurements generation.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.MeasurementBuilder.init` in
                interface :class:`~org.orekit.estimation.measurements.generation.MeasurementBuilder`
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...

_AbstractScheduler__T = typing.TypeVar('_AbstractScheduler__T', bound=org.orekit.estimation.measurements.ObservedMeasurement)  # <T>
class AbstractScheduler(Scheduler[_AbstractScheduler__T], typing.Generic[_AbstractScheduler__T]):
    """
    public abstract class AbstractScheduler<T extends :class:`~org.orekit.estimation.measurements.ObservedMeasurement`<T>> extends :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.estimation.measurements.generation.Scheduler`<T>
    
        Base implementation of :class:`~org.orekit.estimation.measurements.generation.Scheduler` managing
        :class:`~org.orekit.time.DatesSelector`.
    
        Since:
            9.3
    """
    def generate(self, map: typing.Union[java.util.Map[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator], typing.Mapping[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator]]) -> java.util.SortedSet[org.orekit.estimation.measurements.EstimatedMeasurementBase[_AbstractScheduler__T]]: ...
    def getBuilder(self) -> MeasurementBuilder[_AbstractScheduler__T]: ...
    def getSelector(self) -> org.orekit.time.DatesSelector:
        """
            Get the dates selector.
        
            Returns:
                dates selector
        
        
        """
        ...
    def init(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Initialize scheduler at the start of a measurements generation.
        
            This method is called once at the start of the measurements generation. It may be used by the scheduler to initialize
            some internal data if needed, typically :meth:`~org.orekit.estimation.measurements.generation.MeasurementBuilder.init`.
        
            This implementation initialize the measurement builder.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.Scheduler.init` in
                interface :class:`~org.orekit.estimation.measurements.generation.Scheduler`
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...

class GatheringSubscriber(GeneratedMeasurementSubscriber):
    """
    public class GatheringSubscriber extends :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.estimation.measurements.generation.GeneratedMeasurementSubscriber`
    
        Subscriber that gather all generated measurements in a sorted set.
    
        Since:
            12.0
    """
    def __init__(self): ...
    def getGeneratedMeasurements(self) -> java.util.SortedSet[org.orekit.estimation.measurements.EstimatedMeasurementBase[typing.Any]]: ...
    def handleGeneratedMeasurement(self, estimatedMeasurementBase: org.orekit.estimation.measurements.EstimatedMeasurementBase[typing.Any]) -> None:
        """
            Handle a generated measurement.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.GeneratedMeasurementSubscriber.handleGeneratedMeasurement` in
                interface :class:`~org.orekit.estimation.measurements.generation.GeneratedMeasurementSubscriber`
        
            Parameters:
                measurement (:class:`~org.orekit.estimation.measurements.EstimatedMeasurementBase`<?> measurement): measurements that has just been generated
        
        
        """
        ...
    def init(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Initialize subscriber at the start of a measurements generation.
        
            This method is called once at the start of the measurements generation. It may be used by the subscriber to initialize
            some internal data if needed.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.GeneratedMeasurementSubscriber.init` in
                interface :class:`~org.orekit.estimation.measurements.generation.GeneratedMeasurementSubscriber`
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...

class MultiplexedMeasurementBuilder(MeasurementBuilder[org.orekit.estimation.measurements.MultiplexedMeasurement]):
    """
    public class MultiplexedMeasurementBuilder extends :class:`~org.orekit.estimation.measurements.generation.https:.docs.oracle.com.javase.8.docs.api.java.lang.Object?is` implements :class:`~org.orekit.estimation.measurements.generation.MeasurementBuilder`<:class:`~org.orekit.estimation.measurements.MultiplexedMeasurement`>
    
        Builder for :class:`~org.orekit.estimation.measurements.MultiplexedMeasurement` measurements.
    
        Since:
            12.0
    """
    def __init__(self, list: java.util.List[MeasurementBuilder[typing.Any]]): ...
    def addModifier(self, estimationModifier: org.orekit.estimation.measurements.EstimationModifier[org.orekit.estimation.measurements.MultiplexedMeasurement]) -> None: ...
    @typing.overload
    def build(self, absoluteDate: org.orekit.time.AbsoluteDate, spacecraftStateArray: typing.Union[typing.List[org.orekit.propagation.SpacecraftState], jpype.JArray]) -> org.orekit.estimation.measurements.EstimatedMeasurementBase[org.orekit.estimation.measurements.ObservedMeasurement]: ...
    @typing.overload
    def build(self, absoluteDate: org.orekit.time.AbsoluteDate, map: typing.Union[java.util.Map[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator], typing.Mapping[org.orekit.estimation.measurements.ObservableSatellite, org.orekit.propagation.sampling.OrekitStepInterpolator]]) -> org.orekit.estimation.measurements.EstimatedMeasurementBase[org.orekit.estimation.measurements.MultiplexedMeasurement]: ...
    def getModifiers(self) -> java.util.List[org.orekit.estimation.measurements.EstimationModifier[org.orekit.estimation.measurements.MultiplexedMeasurement]]: ...
    def getSatellites(self) -> typing.MutableSequence[org.orekit.estimation.measurements.ObservableSatellite]:
        """
            Get the satellites related to this measurement.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.MeasurementBuilder.getSatellites` in
                interface :class:`~org.orekit.estimation.measurements.generation.MeasurementBuilder`
        
            Returns:
                satellites related to this measurement
        
        
        """
        ...
    def init(self, absoluteDate: org.orekit.time.AbsoluteDate, absoluteDate2: org.orekit.time.AbsoluteDate) -> None:
        """
            Initialize builder at the start of a measurements generation.
        
            This method is called once at the start of the measurements generation. It may be used by the builder to initialize some
            internal data if needed, typically setting up parameters reference dates.
        
            This implementation stores the time span of the measurements generation.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.MeasurementBuilder.init` in
                interface :class:`~org.orekit.estimation.measurements.generation.MeasurementBuilder`
        
            Parameters:
                start (:class:`~org.orekit.time.AbsoluteDate`): start of the measurements time span
                end (:class:`~org.orekit.time.AbsoluteDate`): end of the measurements time span
        
        
        """
        ...

class AngularAzElBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.AngularAzEl]):
    """
    public class AngularAzElBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.AngularAzEl`>
    
        Builder for :class:`~org.orekit.estimation.measurements.AngularAzEl` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, doubleArray: typing.Union[typing.List[float], jpype.JArray], doubleArray2: typing.Union[typing.List[float], jpype.JArray], observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class AngularRaDecBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.AngularRaDec]):
    """
    public class AngularRaDecBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.AngularRaDec`>
    
        Builder for :class:`~org.orekit.estimation.measurements.AngularRaDec` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, frame: org.orekit.frames.Frame, doubleArray: typing.Union[typing.List[float], jpype.JArray], doubleArray2: typing.Union[typing.List[float], jpype.JArray], observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class BistaticRangeBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.BistaticRange]):
    """
    public class BistaticRangeBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.BistaticRange`>
    
        Builder for :class:`~org.orekit.estimation.measurements.BistaticRange` measurements.
    
        Since:
            11.2
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, groundStation2: org.orekit.estimation.measurements.GroundStation, double: float, double2: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class BistaticRangeRateBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.BistaticRangeRate]):
    """
    public class BistaticRangeRateBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.BistaticRangeRate`>
    
        Builder for :class:`~org.orekit.estimation.measurements.BistaticRangeRate` measurements.
    
        Since:
            11.2
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, groundStation2: org.orekit.estimation.measurements.GroundStation, double: float, double2: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

_ContinuousScheduler__T = typing.TypeVar('_ContinuousScheduler__T', bound=org.orekit.estimation.measurements.ObservedMeasurement)  # <T>
class ContinuousScheduler(AbstractScheduler[_ContinuousScheduler__T], typing.Generic[_ContinuousScheduler__T]):
    """
    public class ContinuousScheduler<T extends :class:`~org.orekit.estimation.measurements.ObservedMeasurement`<T>> extends :class:`~org.orekit.estimation.measurements.generation.AbstractScheduler`<T>
    
        :class:`~org.orekit.estimation.measurements.generation.Scheduler` generating measurements sequences continuously.
    
        Continuous schedulers continuously generate measurements following a repetitive pattern. The repetitive pattern can be
        either a continuous stream of measurements separated by a constant step (for example one measurement every 60s), or
        several sequences of measurements at high rate up to a maximum number, with a rest period between sequences (for example
        sequences of up to 256 measurements every 100ms with 300s between each sequence).
    
        Since:
            9.3
    """
    @typing.overload
    def __init__(self, measurementBuilder: MeasurementBuilder[_ContinuousScheduler__T], datesSelector: typing.Union[org.orekit.time.DatesSelector, typing.Callable]): ...
    @typing.overload
    def __init__(self, measurementBuilder: MeasurementBuilder[_ContinuousScheduler__T], datesSelector: typing.Union[org.orekit.time.DatesSelector, typing.Callable], predicate: typing.Union[java.util.function.Predicate[org.orekit.estimation.measurements.EstimatedMeasurementBase[_ContinuousScheduler__T]], typing.Callable[[org.orekit.estimation.measurements.EstimatedMeasurementBase[_ContinuousScheduler__T]], bool]]): ...
    def measurementIsFeasible(self, absoluteDate: org.orekit.time.AbsoluteDate) -> bool:
        """
            Check if a measurement is feasible at some date.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.AbstractScheduler.measurementIsFeasible` in
                class :class:`~org.orekit.estimation.measurements.generation.AbstractScheduler`
        
            Parameters:
                date (:class:`~org.orekit.time.AbsoluteDate`): date to check
        
            Returns:
                true if measurement if feasible
        
        
        """
        ...

_EventBasedScheduler__T = typing.TypeVar('_EventBasedScheduler__T', bound=org.orekit.estimation.measurements.ObservedMeasurement)  # <T>
class EventBasedScheduler(AbstractScheduler[_EventBasedScheduler__T], typing.Generic[_EventBasedScheduler__T]):
    """
    public class EventBasedScheduler<T extends :class:`~org.orekit.estimation.measurements.ObservedMeasurement`<T>> extends :class:`~org.orekit.estimation.measurements.generation.AbstractScheduler`<T>
    
        :class:`~org.orekit.estimation.measurements.generation.Scheduler` based on
        :class:`~org.orekit.propagation.events.EventDetector` for generating measurements sequences.
    
        Event-based schedulers generate measurements following a repetitive pattern when the a
        :class:`~org.orekit.propagation.events.EventDetector` provided at construction is in a
        :class:`~org.orekit.estimation.measurements.generation.SignSemantic` state. It is important that the sign of the g
        function of the underlying event detector is not arbitrary, but has a semantic meaning, e.g. in or out, true or false.
        This class works well with event detectors that detect entry to or exit from a region, e.g.
        :class:`~org.orekit.propagation.events.EclipseDetector`, :class:`~org.orekit.propagation.events.ElevationDetector`,
        :class:`~org.orekit.propagation.events.LatitudeCrossingDetector`. Using this scheduler with detectors that are not based
        on entry to or exit from a region, e.g. :class:`~org.orekit.propagation.events.DateDetector`,
        :class:`~org.orekit.propagation.events.LongitudeCrossingDetector`, will likely lead to unexpected results.
    
        The repetitive pattern can be either a continuous stream of measurements separated by a constant step (for example one
        measurement every 60s), or several sequences of measurements at high rate up to a maximum number, with a rest period
        between sequences (for example sequences of up to 256 measurements every 100ms with 300s between each sequence).
    
        Since:
            9.3
    """
    @typing.overload
    def __init__(self, measurementBuilder: MeasurementBuilder[_EventBasedScheduler__T], datesSelector: typing.Union[org.orekit.time.DatesSelector, typing.Callable], predicate: typing.Union[java.util.function.Predicate[org.orekit.estimation.measurements.EstimatedMeasurementBase[_EventBasedScheduler__T]], typing.Callable[[org.orekit.estimation.measurements.EstimatedMeasurementBase[_EventBasedScheduler__T]], bool]], propagator: org.orekit.propagation.Propagator, eventDetector: org.orekit.propagation.events.EventDetector, signSemantic: SignSemantic): ...
    @typing.overload
    def __init__(self, measurementBuilder: MeasurementBuilder[_EventBasedScheduler__T], datesSelector: typing.Union[org.orekit.time.DatesSelector, typing.Callable], propagator: org.orekit.propagation.Propagator, eventDetector: org.orekit.propagation.events.EventDetector, signSemantic: SignSemantic): ...
    def measurementIsFeasible(self, absoluteDate: org.orekit.time.AbsoluteDate) -> bool:
        """
            Check if a measurement is feasible at some date.
        
            Specified by:
                :meth:`~org.orekit.estimation.measurements.generation.AbstractScheduler.measurementIsFeasible` in
                class :class:`~org.orekit.estimation.measurements.generation.AbstractScheduler`
        
            Parameters:
                date (:class:`~org.orekit.time.AbsoluteDate`): date to check
        
            Returns:
                true if measurement if feasible
        
        
        """
        ...

class FDOABuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.FDOA]):
    """
    public class FDOABuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.FDOA`>
    
        Builder for :class:`~org.orekit.estimation.measurements.FDOA` measurements.
    
        Since:
            12.0
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, groundStation2: org.orekit.estimation.measurements.GroundStation, double: float, double2: float, double3: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class InterSatellitesOneWayRangeRateBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.gnss.InterSatellitesOneWayRangeRate]):
    """
    public class InterSatellitesOneWayRangeRateBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.gnss.InterSatellitesOneWayRangeRate`>
    
        Builder for :class:`~org.orekit.estimation.measurements.gnss.InterSatellitesOneWayRangeRate` measurements.
    
        Since:
            12.1
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite, observableSatellite2: org.orekit.estimation.measurements.ObservableSatellite, double: float, double2: float): ...

class InterSatellitesPhaseBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.gnss.InterSatellitesPhase]):
    """
    public class InterSatellitesPhaseBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.gnss.InterSatellitesPhase`>
    
        Builder for :class:`~org.orekit.estimation.measurements.gnss.InterSatellitesPhase` measurements.
    
        Since:
            10.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite, observableSatellite2: org.orekit.estimation.measurements.ObservableSatellite, double: float, double2: float, double3: float, ambiguityCache: org.orekit.estimation.measurements.gnss.AmbiguityCache): ...

class InterSatellitesRangeBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.InterSatellitesRange]):
    """
    public class InterSatellitesRangeBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.InterSatellitesRange`>
    
        Builder for :class:`~org.orekit.estimation.measurements.InterSatellitesRange` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite, observableSatellite2: org.orekit.estimation.measurements.ObservableSatellite, boolean: bool, double: float, double2: float): ...

class OneWayGNSSPhaseBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.gnss.OneWayGNSSPhase]):
    """
    public class OneWayGNSSPhaseBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.gnss.OneWayGNSSPhase`>
    
        Builder for :class:`~org.orekit.estimation.measurements.gnss.OneWayGNSSPhase` measurements.
    
        Since:
            12.0
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite, observableSatellite2: org.orekit.estimation.measurements.ObservableSatellite, double: float, double2: float, double3: float, ambiguityCache: org.orekit.estimation.measurements.gnss.AmbiguityCache): ...

class OneWayGNSSRangeBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.gnss.OneWayGNSSRange]):
    """
    public class OneWayGNSSRangeBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.gnss.OneWayGNSSRange`>
    
        Builder for :class:`~org.orekit.estimation.measurements.gnss.OneWayGNSSRange` measurements.
    
        Since:
            12.0
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite, observableSatellite2: org.orekit.estimation.measurements.ObservableSatellite, double: float, double2: float): ...

class OneWayGNSSRangeRateBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.gnss.OneWayGNSSRangeRate]):
    """
    public class OneWayGNSSRangeRateBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.gnss.OneWayGNSSRangeRate`>
    
        Builder for :class:`~org.orekit.estimation.measurements.gnss.OneWayGNSSRangeRate` measurements.
    
        Since:
            12.1
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite, observableSatellite2: org.orekit.estimation.measurements.ObservableSatellite, double: float, double2: float): ...

class PVBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.PV]):
    """
    public class PVBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.PV`>
    
        Builder for :class:`~org.orekit.estimation.measurements.PV` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, double: float, double2: float, double3: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class PositionBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.Position]):
    """
    public class PositionBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.Position`>
    
        Builder for :class:`~org.orekit.estimation.measurements.Position` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, double: float, double2: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class RangeBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.Range]):
    """
    public class RangeBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.Range`>
    
        Builder for :class:`~org.orekit.estimation.measurements.Range` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, boolean: bool, double: float, double2: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class RangeRateBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.RangeRate]):
    """
    public class RangeRateBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.RangeRate`>
    
        Builder for :class:`~org.orekit.estimation.measurements.RangeRate` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, boolean: bool, double: float, double2: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class TDOABuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.TDOA]):
    """
    public class TDOABuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.TDOA`>
    
        Builder for :class:`~org.orekit.estimation.measurements.TDOA` measurements.
    
        Since:
            11.2
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, groundStation2: org.orekit.estimation.measurements.GroundStation, double: float, double2: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...

class TurnAroundRangeBuilder(AbstractMeasurementBuilder[org.orekit.estimation.measurements.TurnAroundRange]):
    """
    public class TurnAroundRangeBuilder extends :class:`~org.orekit.estimation.measurements.generation.AbstractMeasurementBuilder`<:class:`~org.orekit.estimation.measurements.TurnAroundRange`>
    
        Builder for :class:`~org.orekit.estimation.measurements.TurnAroundRange` measurements.
    
        Since:
            9.3
    """
    def __init__(self, correlatedRandomVectorGenerator: org.hipparchus.random.CorrelatedRandomVectorGenerator, groundStation: org.orekit.estimation.measurements.GroundStation, groundStation2: org.orekit.estimation.measurements.GroundStation, double: float, double2: float, observableSatellite: org.orekit.estimation.measurements.ObservableSatellite): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("org.orekit.estimation.measurements.generation")``.

    AbstractMeasurementBuilder: typing.Type[AbstractMeasurementBuilder]
    AbstractScheduler: typing.Type[AbstractScheduler]
    AngularAzElBuilder: typing.Type[AngularAzElBuilder]
    AngularRaDecBuilder: typing.Type[AngularRaDecBuilder]
    BistaticRangeBuilder: typing.Type[BistaticRangeBuilder]
    BistaticRangeRateBuilder: typing.Type[BistaticRangeRateBuilder]
    ContinuousScheduler: typing.Type[ContinuousScheduler]
    EventBasedScheduler: typing.Type[EventBasedScheduler]
    FDOABuilder: typing.Type[FDOABuilder]
    GatheringSubscriber: typing.Type[GatheringSubscriber]
    GeneratedMeasurementSubscriber: typing.Type[GeneratedMeasurementSubscriber]
    Generator: typing.Type[Generator]
    InterSatellitesOneWayRangeRateBuilder: typing.Type[InterSatellitesOneWayRangeRateBuilder]
    InterSatellitesPhaseBuilder: typing.Type[InterSatellitesPhaseBuilder]
    InterSatellitesRangeBuilder: typing.Type[InterSatellitesRangeBuilder]
    MeasurementBuilder: typing.Type[MeasurementBuilder]
    MultiplexedMeasurementBuilder: typing.Type[MultiplexedMeasurementBuilder]
    OneWayGNSSPhaseBuilder: typing.Type[OneWayGNSSPhaseBuilder]
    OneWayGNSSRangeBuilder: typing.Type[OneWayGNSSRangeBuilder]
    OneWayGNSSRangeRateBuilder: typing.Type[OneWayGNSSRangeRateBuilder]
    PVBuilder: typing.Type[PVBuilder]
    PositionBuilder: typing.Type[PositionBuilder]
    RangeBuilder: typing.Type[RangeBuilder]
    RangeRateBuilder: typing.Type[RangeRateBuilder]
    Scheduler: typing.Type[Scheduler]
    SignSemantic: typing.Type[SignSemantic]
    TDOABuilder: typing.Type[TDOABuilder]
    TurnAroundRangeBuilder: typing.Type[TurnAroundRangeBuilder]
