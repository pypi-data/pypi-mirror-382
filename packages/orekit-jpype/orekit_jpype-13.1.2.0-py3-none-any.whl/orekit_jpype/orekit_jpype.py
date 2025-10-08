import logging
import jpype
import jpype.imports  # This enables direct import of java classes
from typing import List, Union, Optional
# import jpype.beans  # This creates pythonic versions of getters / setters (as in JCC version)

import os

# Get the  path of the current file, used for finding the jars directory
dirpath = os.path.dirname(os.path.abspath(__file__))


def initVM(vmargs: Union[str, None] = None,
           additional_classpaths: Union[List, None] = None,
           jvmpath: Optional[Union[str, os.PathLike]] = None):
    """
    Initializes the Java Virtual Machine (JVM) for Orekit.

    Args:
        vmargs (Union[str, None], optional): Additional arguments to pass to the JVM. Defaults to None.
             Example for debugging: vmargs='-Xcheck:jni,-verbose:jni,-verbose:class,-XX:+UnlockDiagnosticVMOptions'
        additional_classpaths (Union[List, None], optional): Additional classpaths to add to the JVM. Defaults to None.
        jvmpath (Union[str, os.PathLike], optional): Path to the jvm library file,
            Typically one of (``libjvm.so``, ``jvm.dll``, ...)
            Defaults to None, in this case Jpype will look for a JDK on the system.

    Raises:
        FileNotFoundError: If any of the additional classpaths do not exist.

    """
    # Set the classpath
    if additional_classpaths is not None:
        for classpath in additional_classpaths:
            if not os.path.exists(classpath):
                raise FileNotFoundError(f"Classpath {os.path.abspath(classpath)} does not exist")
            jpype.addClassPath(os.path.abspath(classpath))

    # Add standard orekit jars to the classpath
    if not jpype.isJVMStarted():
        jpype.addClassPath(os.path.join(dirpath, 'jars', '*'))

        # Assemble JVM argument list
        args = ["-XX:TieredStopAtLevel=1"]          # <-- disable C2 JIT
        if vmargs:
            args.extend(arg.strip() for arg in vmargs.split(",") if arg.strip())

        # Avoid double‑injecting the flag if caller already passed it
        args = list(dict.fromkeys(args))            # preserves order, removes dups


        # Start the JVM
        # '-Xcheck:jni','-verbose:jni','-verbose:class'
        jpype.startJVM(*args, convertStrings=True, jvmpath=jvmpath)
        logging.debug(f"JVM started, using: {jpype.getDefaultJVMPath()}")
    else:
        logging.debug("JVM already running, resuming on existing JVM")

    # get java version
    java_major_version,_,_ = jpype.getJVMVersion()

    if jpype.__version__ >= '1.6.0' and java_major_version < 11:
        raise RuntimeError(f"Orekit dependency Jpype {jpype.__version__} requires Java 11 or higher, but found Java {java_major_version}.")

    # Perform modifications for orekit
    import orekit_jpype.orekit_converters  # noqa: F401
