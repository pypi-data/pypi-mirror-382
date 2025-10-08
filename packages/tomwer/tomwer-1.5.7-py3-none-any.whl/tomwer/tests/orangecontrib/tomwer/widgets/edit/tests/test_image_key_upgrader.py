# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017-2019 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "10/12/2021"


import gc

import pytest
from silx.gui import qt
from silx.gui.utils.testutils import TestCaseQt

from orangecontrib.tomwer.widgets.edit.ImageKeyUpgraderOW import ImageKeyUpgraderOW
from tomwer.tests.utils import skip_gui_test


@pytest.mark.skipif(skip_gui_test(), reason="skip gui test")
class TestImageKeyEditor(TestCaseQt):
    """Test that the ImageKeyUpgraderOW widget work correctly. Processing test are done in the core module. gui test are done in the tomwer.gui.edit module"""

    def setUp(self):
        super().setUp()
        self._window = ImageKeyUpgraderOW()

    def tearDown(self):
        self._window.setAttribute(qt.Qt.WA_DeleteOnClose)
        self._window.close()
        self._window = None
        gc.collect()

    def test(self):
        self._window.show()
        self.qWaitForWindowExposed(self._window)
