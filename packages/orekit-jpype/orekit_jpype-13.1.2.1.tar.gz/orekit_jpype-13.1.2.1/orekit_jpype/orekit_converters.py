"""
This file contains a number of tweaks in order to tune orekit with jpype according to preferences.

It is assumed that the JVM is running.
Importing this file will automatically implement the changes.

"""

import datetime
import orekit_jpype


from jpype._jcustomizer import JImplementationFor, JConversion
import _jpype

from jpype.types import JArray, JDouble

from orekit_jpype.pyhelpers import absolutedate_to_datetime, datetime_to_absolutedate

import numpy as np

import os
dirpath = os.path.dirname(os.path.abspath(__file__))


# Change representation of object (__repr__) to include toString()
def _JObjectRepr(obj) -> str:
    # Function to generate the __repr__ string for objects in interactive mode

    return f"<{obj.getClass().getSimpleName()}: {obj.toString()}>"


# Monkey patch the base class
_jpype._JObject.__repr__ = _JObjectRepr

# Create a top level function JArray_double to mimic JCC backend
orekit_jpype.JArray_double = JArray(JDouble)


# Some helper methods on selected classes
@JImplementationFor("org.orekit.time.AbsoluteDate")
class _JAbsoluteDate(object):

    def to_datetime(self) -> datetime.datetime:
        """

        Returns: The AbsoluteDate as a Python datetime

        """
        return absolutedate_to_datetime(self)

    @JImplementationFor("double[][]")
    class _JDouble2DArray(object):

        def to_numpy(self) -> np.ndarray:
            """
            Get the Java Double 2D Array as a Python numpy array

            Returns: the Double Array as numpy 2D array

            """
            return np.array(self)

        def __repr__(self):
            np_2darray_prettier = str(self.to_numpy()).replace('\n', ',')
            return f"<{self.getClass().getSimpleName()}: {np_2darray_prettier}>"

    @JImplementationFor("double[]")
    class _JDoubleArray(object):
        def to_numpy(self):
            """
            Get the Java Double Array as a Python numpy array
            Returns: the Double Array as numpy array
            """
            return np.array(self)

        def __repr__(self):
            return f"<{self.getClass().getSimpleName()}: {self.to_numpy()}>"


# Conversions
@JConversion("org.orekit.time.AbsoluteDate", instanceof=datetime.datetime)
def _JADConversion(jcls, obj):
    return datetime_to_absolutedate(obj)
