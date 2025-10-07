import asyncio
import argparse
import sys
import runpy

from typing import Sequence

def invoke_direct(*args):
    """
    Invoke the flashtool with a bare list of arguments
    """
    # The __main__ of the upstream isn't function wrapped, so it would be nice to extract it with ast (or call it with reflection magic)
    # However, becase I want basic function, it's excerpted here.
    ### BEGIN EXCERPT
    parser = argparse.ArgumentParser(
        description="Katapult Flash Tool")
    parser.add_argument(
        "-d", "--device", metavar='<serial device>',
        help="Serial Device"
    )
    parser.add_argument(
        "-b", "--baud", default=250000, metavar='<baud rate>',
        help="Serial baud rate"
    )
    parser.add_argument(
        "-i", "--interface", default="can0", metavar='<can interface>',
        help="Can Interface"
    )
    parser.add_argument(
        "-f", "--firmware", metavar="<klipper.bin>",
        default="~/klipper/out/klipper.bin",
        help="Path to Klipper firmware file")
    parser.add_argument(
        "-u", "--uuid", metavar="<uuid>", default=None,
        help="Can device uuid"
    )
    parser.add_argument(
        "-q", "--query", action="store_true",
        help="Query available CAN UUIDs (CANBus Ony)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Enable verbose responses"
    )
    parser.add_argument(
        "-r", "--request-bootloader", action="store_true",
        help="Requests the bootloader and exits"
    )
    parser.add_argument(
        "-s", "--status", action="store_true",
        help="Connect to bootloader and print status"
    )
    ### END EXCERPT
    flashtool_args = parser.parse_args(args=args)
    # TODO: Some extra sanity checks here
    # We delay this import until here to allow for fast failure
    # TODO: Wrap this in a try to detect misbuilt packages
    from .flashtool import main as flashtool_main
    return(asyncio.run(flashtool_main(flashtool_args)))


def invoke_raw():
    """
    Invoke the main of flashtool. This will not return. Args will be read from sys.argv.
    """
    runpy.run_module('kataflash.upstream.flashtool', run_name='__main__', alter_sys=True)


def invoke_args(*args: Sequence[str]):
    """
    Invoke the main of flashtool with the given args. This will not return.
    """
    arg0 = sys.argv[0]
    sys.argv = [arg0, *args]
    invoke_raw()

def invoke(*args):
    old_argv = sys.argv.copy()
    try:
        invoke_args(*args)
    except SystemExit as e:
        # invoke_args will overwrite the args to get argparse to do what we want, this is needed to restore it
        # We do this inplace just in case something else has a ref to this around
        sys.argv.clear()
        sys.argv += old_argv
        return e.args[0]


