import pytest

import src.ac100 as ac100
import src.definitions as defs
import src.exceptions as ac_exc

parser = ac100.parser
ac100.setup_parser(parser)

class TestCommandLineArgs:
    def test_negative_height(self):
        testargs = ["out", "-r", "-1"]
        arg_namespace = parser.parse_args(testargs)
        with pytest.raises(ac_exc.NegativeVideoDimensionError):
            ac100.check_video_dimensions(arg_namespace)

    def test_height_too_big(self):
        testargs = ["out", "-r", "20000"]
        arg_namespace = parser.parse_args(testargs)
        with pytest.raises(ac_exc.VRAMTooLargeError):
            ac100.check_video_dimensions(arg_namespace)

    def test_negative_width(self):
        testargs = ["out", "-c", "-1"]
        arg_namespace = parser.parse_args(testargs)
        with pytest.raises(ac_exc.NegativeVideoDimensionError):
            ac100.check_video_dimensions(arg_namespace)

    def test_width_too_big(self):
        testargs = ["out", "-c", "20000"]
        arg_namespace = parser.parse_args(testargs)
        with pytest.raises(ac_exc.VRAMTooLargeError):
            ac100.check_video_dimensions(arg_namespace)
