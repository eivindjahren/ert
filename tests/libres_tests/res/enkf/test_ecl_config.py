#!/usr/bin/env python
#  Copyright (C) 2013  Equinor ASA, Norway.
#
#  This file is part of ERT - Ensemble based Reservoir Tool.
#
#  ERT is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ERT is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.
#
#  See the GNU General Public License at <http://www.gnu.org/licenses/gpl.html>
#  for more details.

import os.path
from datetime import datetime

from ecl.summary import EclSum
from ecl.util.test import TestAreaContext

from res.enkf import ConfigKeys, EclConfig, ResConfig
from res.util import UIReturn


def test_grid(source_root):
    grid_file = source_root / "test-data/local/snake_oil_field/grid/CASE.EGRID"
    smspec_file = (
        source_root / "test-data/local/snake_oil_field/refcase/SNAKE_OIL_FIELD.SMSPEC"
    )
    ec = EclConfig()
    ui = ec.validateGridFile(str(grid_file))
    assert ui
    assert isinstance(ui, UIReturn)

    ui = ec.validateGridFile("Does/Not/Exist")
    assert not ui

    assert os.path.exists(smspec_file)
    ui = ec.validateGridFile(str(smspec_file))
    assert not ui


def test_datafile(source_root):
    ec = EclConfig()
    ui = ec.validateDataFile("DoesNotExist")
    assert not ui

    dfile = str(source_root / "test-data/local/eclipse/SPE1.DATA")
    ui = ec.validateDataFile(dfile)
    assert ui
    ec.setDataFile(dfile)
    assert dfile == ec.getDataFile()


def test_refcase(source_root):
    ec = EclConfig()
    dfile = str(source_root / "test-data/local/snake_oil/refcase/SNAKE_OIL_FIELD")

    ui = ec.validateRefcase("Does/not/exist")
    assert not ui

    ui = ec.validateRefcase(dfile)
    assert ui
    ec.loadRefcase(dfile)
    refcase = ec.getRefcase()
    assert isinstance(refcase, EclSum)
    refcaseName = ec.getRefcaseName()
    assert dfile == refcaseName


def test_wrongly_configured_refcase_path():
    config_dict = {
        ConfigKeys.REFCASE: "this/is/not/REFCASE",
    }
    ecl_config = EclConfig(config_dict=config_dict)
    assert ecl_config.getRefcaseName() is None
    assert ecl_config.getRefcase() is None


def test_ecl_config_constructor(source_root):
    config_dict = {
        ConfigKeys.DATA_FILE: "configuration_tests/input/SPE1.DATA",
        ConfigKeys.ECLBASE: "configuration_tests/input/<ECLIPSE_NAME>-%d",
        ConfigKeys.GRID: "configuration_tests/input/CASE.EGRID",
        ConfigKeys.REFCASE: "configuration_tests/input/refcase/SNAKE_OIL_FIELD",
        ConfigKeys.SCHEDULE_PREDICTION_FILE: ("configuration_tests/input/schedule.sch"),
    }

    case_directory = str(source_root / "test-data/local/configuration_tests/")
    with TestAreaContext("ecl_config_test") as work_area:
        work_area.copy_directory(case_directory)
        res_config = ResConfig("configuration_tests/ecl_config.ert")
        ecl_config_file = res_config.ecl_config
        ecl_config_dict = EclConfig(config_dict=config_dict)

        assert ecl_config_dict == ecl_config_file


def test_that_refcase_gets_correct_name(tmpdir):
    config_dict = {
        ConfigKeys.REFCASE: "MY_REFCASE",
    }

    with tmpdir.as_cwd():
        # Create a refcase
        ecl_sum = EclSum.writer("MY_REFCASE", datetime(2014, 9, 10), 10, 10, 10)
        ecl_sum.addVariable("FOPR", unit="SM3/DAY")
        t_step = ecl_sum.addTStep(2, sim_days=1)
        t_step["FOPR"] = 1
        ecl_sum.fwrite()

        ecl_config = EclConfig(config_dict=config_dict)
        assert ecl_config.getRefcaseName() == tmpdir / "MY_REFCASE"
