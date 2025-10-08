# SPDX-FileCopyrightText: 2025 PairInteraction Developers
# SPDX-License-Identifier: LGPL-3.0-or-later


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pairinteraction.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

import multiprocessing
import sys

from pairinteraction_gui.app import Application
from pairinteraction_gui.main_window import MainWindow

__all__ = ["main"]


def main() -> int:
    """Run the PairInteraction GUI application.

    Returns:
        int: Application exit code

    """
    # Multithreading together with "fork" is not supported
    # (up to python 3.14 "fork" was the default on linux
    # see also https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
    # and https://docs.python.org/3.14/whatsnew/3.14.html#whatsnew314-multiprocessing-start-method)
    # We set the start method to "spawn" for all platforms (anyway default on mac and windows)
    # TODO instead of multiprocessing it would probably be better to release the GIL during some C++ calls
    # see here: https://nanobind.readthedocs.io/en/latest/api_core.html#_CPPv4N8nanobind18gil_scoped_releaseE
    multiprocessing.set_start_method("spawn")

    app = Application(sys.argv)
    app.setApplicationName("PairInteraction")

    app.allow_ctrl_c()

    window = MainWindow()
    window.show()

    return app.exec()
