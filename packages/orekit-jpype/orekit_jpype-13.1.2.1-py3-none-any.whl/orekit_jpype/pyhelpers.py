# encoding: utf-8

#   Copyright 2014 SSC
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

# This document contains classes that are useful for using the orekit
# library in Python.

import shutil
from datetime import datetime, timedelta, timezone

import math
import os
import logging
from typing import List, Union
import numpy as np
import numpy.typing as npt

from jpype.types import JArray, JDouble

from java.io import File
from org.orekit.data import ZipJarCrawler, DirectoryCrawler, DataContext, LazyLoadedDataContext
from org.orekit.time import TimeScalesFactory, AbsoluteDate, TimeOffset
from org.orekit.frames import FramesFactory
from org.orekit.utils import ElevationMask
from org.orekit.bodies import CelestialBodyFactory
from java.lang.reflect import Modifier
from java.util import Map
from java.util.concurrent import TimeUnit

try:
    import urllib.request as urlrequest
except ImportError:
    import urllib as urlrequest


def download_orekit_data_curdir(filename='orekit-data.zip'):
    """
    Orekit needs a number of orientation and model parameters. An example file is available on the
    orekit gitlab. This funciton downloads that file to the current directory.

    Note that for non-testing purposes, this file should

    Args:
        filename (str): Store the downloaded data as this filename/path. Default is "orekit-data.zip"
    """
    url = "https://gitlab.orekit.org/orekit/orekit-data/-/archive/main/orekit-data-main.zip"
    # Download the orekit-data file and store it locally

    with urlrequest.urlopen(url) as response, open(filename, 'wb') as out_file:
        logging.info(f"Downloading orekit data file from: {url}")
        shutil.copyfileobj(response, out_file)



def clear_factory_maps(factory_class):
    for field in factory_class.getDeclaredFields():
        if Modifier.isStatic(field.getModifiers()) and Map.class_.isAssignableFrom(field.getType()):
            field.setAccessible(True)
            field.get(None).clear()


def clear_factories():
    DataContext.setDefault(LazyLoadedDataContext())
    clear_factory_maps(CelestialBodyFactory.class_)
    CelestialBodyFactory.clearCelestialBodyLoaders()
    clear_factory_maps(FramesFactory.class_)


def setup_orekit_curdir(filename: str = 'orekit-data.zip', from_pip_library: bool = False):
    """Setup the java engine with orekit.

    This function loads the Orekit data from either:
        - A zip in the current directory (by default orekit-data.zip),
        - A folder,
        - From the `orekitdata` Python library, installable via pip (see below)
    depending on whether `filename` is the path to a file or to a folder, and whether from_pip_library is True or False

    The `orekitdata` library is installable with `pip install git+https://gitlab.orekit.org/orekit/orekit-data.git`
s
    Then the function sets up the Orekit DataProviders to access it.

    The JVM needs to be initiated prior to calling this function:

        orekit.initVM()

    Args:
        filename (str): Name of zip or folder with orekit data. Default filename is 'orekit-data.zip'
        from_pip_library (bool), default False: if True, will first try to load the data from the `orekitdata` python library

    """

    DM = DataContext.getDefault().getDataProvidersManager()

    data_load_from_library_sucessful = False
    if from_pip_library:
        try:
            import orekitdata
            datafile = File(orekitdata.__path__[0])
            if not datafile.exists():
                logging.info(f"""Unable to find orekitdata library folder,
                      will try to load Orekit data using the folder or filename {filename}""")
            else:
                filename = orekitdata.__path__[0]
                data_load_from_library_sucessful = True
        except ImportError as e:
            logging.warning(f"""Failed to load orekitdata library.
                  Install with `pip install git+https://gitlab.orekit.org/orekit/orekit-data.git`
                  Will try to load Orekit data using the folder or filename {filename}""")


    if not data_load_from_library_sucessful:
        if filename is None:
            logging.warning("filename argument was None, unable to load orekit data from file or folder")
            raise FileNotFoundError("filename argument was None, unable to load orekit data from file or folder")

        datafile = File(filename)
        if not datafile.exists():
            logging.warning(f"File or folder: {datafile.getAbsolutePath()} not found")
            logging.warning("""

            The Orekit library relies on some external data for physical models.
            Typical data are the Earth Orientation Parameters and the leap seconds history,
            both being provided by the IERS or the planetary ephemerides provided by JPL.
            Such data is stored in text or binary files with specific formats that Orekit knows
            how to read, and needs to be provided for the library to work.

            You can download a starting file with this data from the orekit gitlab at:
            https://gitlab.orekit.org/orekit/orekit-data

            or by the function:
            orekit.pyhelpers.download_orekit_data_curdir()

            """)

            raise FileNotFoundError(datafile.getAbsolutePath())


    logging.debug(f"Loading Orekit data from: {datafile.getAbsolutePath()}")
    if os.path.isdir(filename):
        crawler = DirectoryCrawler(datafile)
    elif os.path.isfile(filename):
        crawler = ZipJarCrawler(datafile)
    else:
        logging.warning(f'Could not load orekit data from filename: {filename}')
        raise FileNotFoundError(filename)

    DM.clearProviders()
    DM.clearLoadedDataNames()
    DM.resetFiltersToDefault()
    DM.addProvider(crawler)


def setup_orekit_data(filenames: Union[str, List[str], None] = 'orekit-data.zip', from_pip_library: bool = True) -> None:
    """
    Sets up the orekit data from a file, folder or list of files/folders.
    Can also load the data from the `orekitdata` python library. (default)

    Args:
        filenames (Union[str, List[str]]): Name of zip or folder with orekit data. Default filename is 'orekit-data.zip'
        from_pip_library (bool), default True: if True, will first try to load the data from the `orekitdata` python library

    """

    setup_orekit_curdir(filename=filenames, from_pip_library=from_pip_library)


MICROSECOND_MULTIPLIER = 1000000
def absolutedate_to_datetime(orekit_absolutedate: AbsoluteDate, tz_aware=False) -> datetime:
    """ Converts from orekit.AbsoluteDate objects
    to python datetime objects (utc).

    Args:
        orekit_absolutedate (AbsoluteDate): orekit AbsoluteDate object to convert
        tz_aware (bool): If True, the returned datetime will be timezone-aware (UTC). Default is False.
    Returns:
        datetime: time in python datetime format (UTC)
    """

    utc = TimeScalesFactory.getUTC()
    or_comp = orekit_absolutedate.getComponents(utc)
    or_date = or_comp.getDate()
    or_time = or_comp.getTime()
    us = or_time.getSplitSecond().getRoundedTime(TimeUnit.MICROSECONDS)
    dt = datetime(or_date.getYear(),
                    or_date.getMonth(),
                    or_date.getDay(),
                    or_time.getHour(),
                    or_time.getMinute()) + timedelta(microseconds=us)
    if tz_aware:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

def datetime_to_absolutedate(dt_date: datetime) -> AbsoluteDate:
    """
    Converts from python datetime objects to orekit AbsoluteDate objects.

    Args:
        dt_date (datetime): datetime object to convert
    Returns:
        AbsoluteDate: time in orekit AbsoluteDate format
    """
    if dt_date.tzinfo is not None and dt_date.tzinfo.utcoffset(dt_date) is not None:
        # If the datetime is timezone-aware, convert it to UTC
        dt_date = dt_date.astimezone(timezone.utc)

    utc = TimeScalesFactory.getUTC()

    return AbsoluteDate(dt_date.year,
                        dt_date.month,
                        dt_date.day,
                        dt_date.hour,
                        dt_date.minute,
                        TimeOffset(dt_date.second*MICROSECOND_MULTIPLIER+dt_date.microsecond, TimeOffset.MICROSECOND),
                        utc)


def to_elevationmask(az: List[float], el: List[float]) -> ElevationMask:
    """ Converts an array of azimuths and elevations to a
    orekit ElevationMask object. All units in degrees.

        mask = to_elevationmask([0, 90, 180, 270], [5,10,8,5])

    """
    double_2darray = JArray_double2D(
        np.vstack((
            np.deg2rad(az),
            np.deg2rad(el)
        )).T
    )

    return ElevationMask(double_2darray)


def np_to_JArray_double(array: npt.NDArray[np.float64]) -> JArray:
    """
    Converts a N-dimensional numpy array of doubles to a JArray of doubles
    Inspired from
        https://github.com/jpype-project/jpype/blob/653ccffd1df46e4d472217d77f592326ae3d3690/test/jpypetest/test_buffer.py#L187
    """
    return JArray(JDouble, array.ndim)(array)


def JArray_double2D(array: npt.NDArray[np.float64]) -> JArray:
    """
    This function name is kept for backwards compatibility but it actually just calls np_to_JArray_double
    """
    return np_to_JArray_double(array=array)


def JArray_double1D(array: npt.NDArray[np.float64]) -> JArray:
    """
    This function just calls np_to_JArray_double to convert a 1D numpy array to a JArray
    """
    return np_to_JArray_double(array=array)
