import pytest

import src.ac100 as ac100
import src.definitions as defs
import src.exceptions as ac_exc

parser = ac100.parser
ac100.setup_parser(parser)

class TestEmuCommandLineArgs:
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

    def test_row_ok(self):
        testargs = ["out", "-r", "20"]
        arg_namespace = parser.parse_args(testargs)
        dimensions = ac100.check_video_dimensions(arg_namespace)
        assert dimensions[0] == 20, "Didn't set rows correctly"
        assert dimensions[1] == defs.DEFAULT_VIDEO_COLUMNS, "Should not have "\
            f"changed width from {defs.DEFAULT_VIDEO_COLUMNS} to {dimensions[1]}"

    def test_column_ok(self):
        testargs = ["out", "-c", "20"]
        arg_namespace = parser.parse_args(testargs)
        dimensions = ac100.check_video_dimensions(arg_namespace)
        assert dimensions[0] == defs.DEFAULT_VIDEO_ROWS, "Should not have "\
            f"changed height from {defs.DEFAULT_VIDEO_ROWS} to {dimensions[0]}"
        assert dimensions[1] == 20, "Didn't set columns correctly"

    def test_both_dimensions_ok(self):
        testargs = ["out", "-c", "20", "-r", "20"]
        arg_namespace = parser.parse_args(testargs)
        dimensions = ac100.check_video_dimensions(arg_namespace)
        assert dimensions[0] == 20, "Didn't set rows correctly"
        assert dimensions[1] == 20, "Didn't set columns correctly"

    def test_vram_negative_column(self):
        machine = ac100.AC100()
        logger = ac100.logger
        testargs = ["out", "-c", "-1"]
        arg_namespace = parser.parse_args(testargs)
        ac100.setup_logger(logger, arg_namespace)
        # method handles exception, so we should see dimensions at their default
        # values
        machine.initialize_VRAM(arg_namespace)
        assert machine.VIDEO_HEIGHT == defs.DEFAULT_VIDEO_ROWS
        assert machine.VIDEO_WIDTH == defs.DEFAULT_VIDEO_COLUMNS

    def test_vram_negative_row(self):
        machine = ac100.AC100()
        logger = ac100.logger
        testargs = ["out", "-r", "-1"]
        arg_namespace = parser.parse_args(testargs)
        ac100.setup_logger(logger, arg_namespace)
        # method handles exception, so we should see dimensions at their default
        # values
        machine.initialize_VRAM(arg_namespace)
        assert machine.VIDEO_HEIGHT == defs.DEFAULT_VIDEO_ROWS
        assert machine.VIDEO_WIDTH == defs.DEFAULT_VIDEO_COLUMNS

    def test_vram_display_too_wide(self):
        machine = ac100.AC100()
        logger = ac100.logger
        testargs = ["out", "-c", "20000"]
        arg_namespace = parser.parse_args(testargs)
        ac100.setup_logger(logger, arg_namespace)
        # method handles exception, so we should see dimensions at their default
        # values
        machine.initialize_VRAM(arg_namespace)
        assert machine.VIDEO_HEIGHT == defs.DEFAULT_VIDEO_ROWS
        assert machine.VIDEO_WIDTH == defs.DEFAULT_VIDEO_COLUMNS

    def test_vram_display_too_tall(self):
        machine = ac100.AC100()
        logger = ac100.logger
        testargs = ["out", "-r", "20000"]
        arg_namespace = parser.parse_args(testargs)
        ac100.setup_logger(logger, arg_namespace)
        # method handles exception, so we should see dimensions at their default
        # values
        machine.initialize_VRAM(arg_namespace)
        assert machine.VIDEO_HEIGHT == defs.DEFAULT_VIDEO_ROWS
        assert machine.VIDEO_WIDTH == defs.DEFAULT_VIDEO_COLUMNS

    def test_vram_height_ok(self):
        machine = ac100.AC100()
        logger = ac100.logger
        testargs = ["out", "-r", "20"]
        arg_namespace = parser.parse_args(testargs)
        ac100.setup_logger(logger, arg_namespace)
        machine.initialize_VRAM(arg_namespace)
        assert machine.VIDEO_HEIGHT == 20
        assert machine.VIDEO_WIDTH == defs.DEFAULT_VIDEO_COLUMNS

    def test_vram_width_ok(self):
        machine = ac100.AC100()
        logger = ac100.logger
        testargs = ["out", "-c", "20"]
        arg_namespace = parser.parse_args(testargs)
        ac100.setup_logger(logger, arg_namespace)
        machine.initialize_VRAM(arg_namespace)
        assert machine.VIDEO_HEIGHT == defs.DEFAULT_VIDEO_ROWS
        assert machine.VIDEO_WIDTH == 20

    def test_vram_both_ok(self):
        machine = ac100.AC100()
        logger = ac100.logger
        testargs = ["out", "-c", "20", "-r", "20"]
        arg_namespace = parser.parse_args(testargs)
        ac100.setup_logger(logger, arg_namespace)
        machine.initialize_VRAM(arg_namespace)
        assert machine.VIDEO_HEIGHT == 20
        assert machine.VIDEO_WIDTH == 20
