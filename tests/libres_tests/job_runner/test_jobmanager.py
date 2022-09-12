import json
import os
import os.path
import stat

import pytest

from ert._c_wrappers.job_queue import (
    EnvironmentVarlist,
    ExtJob,
    ExtJoblist,
    ForwardModel,
)
from ert._c_wrappers.util import SubstitutionList
from ert.job_runner.reporting.message import Exited, Start
from ert.job_runner.runner import JobRunner

# Test data generated by ForwardModel
JSON_STRING = """
{
  "DATA_ROOT" : "/path/to/data",
  "run_id"    : "ERT_RUN_ID",
  "umask" : "0000",
  "jobList" : [ {"name" : "PERLIN",
  "executable" : "perlin.py",
  "target_file" : "my_target_file",
  "error_file" : "error_file",
  "start_file" : "some_start_file",
  "stdout" : "perlin.stdoit",
  "stderr" : "perlin.stderr",
  "stdin" : "intput4thewin",
  "argList" : ["-speed","hyper"],
  "environment" : {"TARGET" : "flatland"},
  "license_path" : "this/is/my/license/PERLIN",
  "max_running_minutes" : 12,
  "max_running" : 30
},
{"name" : "PERGEN",
  "executable" : "pergen.py",
  "target_file" : "my_target_file",
  "error_file" : "error_file",
  "start_file" : "some_start_file",
  "stdout" : "perlin.stdoit",
  "stderr" : "perlin.stderr",
  "stdin" : "intput4thewin",
  "argList" : ["-speed","hyper"],
  "environment" : {"TARGET" : "flatland"},
  "license_path" : "this/is/my/license/PERGEN",
  "max_running_minutes" : 12,
  "max_running" : 30
}]
}
"""

JSON_STRING_NO_DATA_ROOT = """
{
  "umask" : "0000",
  "jobList"   : []
}
"""


def create_jobs_json(job_list, umask="0000"):
    return {"umask": umask, "DATA_ROOT": "/path/to/data", "jobList": job_list}


@pytest.fixture(autouse=True)
def set_up_environ():
    if "DATA_ROOT" in os.environ:
        del os.environ["DATA_ROOT"]

    if "ERT_RUN_ID" in os.environ:
        del os.environ["ERT_RUN_ID"]

    yield

    keys = (
        "KEY_ONE",
        "KEY_TWO",
        "KEY_THREE",
        "KEY_FOUR",
        "PATH104",
        "DATA_ROOT",
        "ERT_RUN_ID",
    )

    for key in keys:
        if key in os.environ:
            del os.environ[key]


@pytest.mark.usefixtures("setup_tmpdir")
def test_missing_joblist_json():
    with pytest.raises(KeyError):
        JobRunner({"umask": "0000"})


@pytest.mark.usefixtures("setup_tmpdir")
def test_missing_umask_json():
    with pytest.raises(KeyError):
        JobRunner({"jobList": "[]"})


@pytest.mark.usefixtures("setup_tmpdir")
def test_run_output_rename():
    job = {
        "name": "TEST_JOB",
        "executable": "/bin/mkdir",
        "stdout": "out",
        "stderr": "err",
    }
    joblist = [job, job, job, job, job]

    jobm = JobRunner(create_jobs_json(joblist))

    for status in enumerate(jobm.run([])):
        if isinstance(status, Start):
            assert status.job.std_err == f"err.{status.job.index}"
            assert status.job.std_out == f"out.{status.job.index}"


@pytest.mark.usefixtures("setup_tmpdir")
def test_run_multiple_ok():
    joblist = []
    dir_list = ["1", "2", "3", "4", "5"]
    for job_index in dir_list:
        job = {
            "name": "MKDIR",
            "executable": "/bin/mkdir",
            "stdout": f"mkdir_out.{job_index}",
            "stderr": f"mkdir_err.{job_index}",
            "argList": ["-p", "-v", job_index],
        }
        joblist.append(job)

    jobm = JobRunner(create_jobs_json(joblist))

    statuses = [s for s in list(jobm.run([])) if isinstance(s, Exited)]

    assert len(statuses) == 5
    for status in statuses:
        assert status.exit_code == 0

    for dir_number in dir_list:
        assert os.path.isdir(dir_number)
        assert os.path.isfile(f"mkdir_out.{dir_number}")
        assert os.path.isfile(f"mkdir_err.{dir_number}")
        assert 0 == os.path.getsize(f"mkdir_err.{dir_number}")


@pytest.mark.usefixtures("setup_tmpdir")
def test_run_multiple_fail_only_runs_one():
    joblist = []
    for index in range(1, 6):
        job = {
            "name": "exit",
            "executable": "/bin/bash",
            "stdout": "exit_out",
            "stderr": "exit_err",
            # produces something on stderr, and exits with
            "argList": [
                "-c",
                f'echo "failed with {index}" 1>&2 ; exit {index}',
            ],
        }
        joblist.append(job)

    jobm = JobRunner(create_jobs_json(joblist))

    statuses = [s for s in list(jobm.run([])) if isinstance(s, Exited)]

    assert len(statuses) == 1
    for i, status in enumerate(statuses):
        assert status.exit_code == i + 1


@pytest.mark.usefixtures("setup_tmpdir")
def test_given_global_env_and_update_path_executable_env_is_updated():
    executable = "./x.py"
    outfile = "outfile.stdout.0"

    with open(executable, "w") as f:
        f.write("#!/usr/bin/env python\n")
        f.write("import os\n")
        f.write("print(os.environ['KEY_ONE'])\n")
        f.write("print(os.environ['KEY_TWO'])\n")
        f.write("print(os.environ['PATH104'])\n")
        f.write("print(os.environ['KEY_THREE'])\n")
        f.write("print(os.environ['KEY_FOUR'])\n")
    os.chmod(executable, stat.S_IEXEC + stat.S_IREAD)

    job = {
        "name": "TEST_GET_ENV1",
        "executable": executable,
        "stdout": outfile,
        "stderr": "outfile.stderr.0",
        "argList": [],
    }

    data = {
        "umask": "0000",
        "global_environment": {
            "KEY_ONE": "FirstValue",
            "KEY_TWO": "SecondValue",
            "KEY_THREE": "ThirdValue",
            "KEY_FOUR": "ThirdValue:FourthValue",
        },
        "global_update_path": {
            "PATH104": "NewPath",
            "KEY_THREE": "FourthValue",
            "KEY_FOUR": "FifthValue:SixthValue",
        },
        "DATA_ROOT": "/path/to/data",
        "jobList": [job],
    }

    statuses = list(JobRunner(data).run([]))

    exited_messages = [m for m in statuses if isinstance(m, Exited) and m.success()]
    number_of_finished_scripts = len(exited_messages)
    assert (
        number_of_finished_scripts == 1
    ), "guard check, script must finish successfully"

    with open(outfile, "r") as out0:
        content = list(out0.read().splitlines())
        assert content[0] == "FirstValue"
        assert content[1] == "SecondValue"
        assert content[2] == "NewPath"
        assert content[3] == "FourthValue:ThirdValue"
        assert (
            content[4] == "FifthValue:SixthValue:ThirdValue:FourthValue"
        ), "should be a concatenation of the variable from environment and update_path"


@pytest.mark.usefixtures("setup_tmpdir")
def test_exec_env():
    with open("exec_env.py", "w") as f:
        f.write(
            """#!/usr/bin/env python\n
import os
import json
with open("exec_env_exec_env.json") as f:
 exec_env = json.load(f)
assert exec_env["TEST_ENV"] == "123"
assert exec_env["NOT_SET"] is None
            """
        )
    os.chmod("exec_env.py", stat.S_IEXEC + stat.S_IREAD)

    with open("EXEC_ENV", "w") as f:
        f.write("EXECUTABLE exec_env.py\n")
        f.write("EXEC_ENV TEST_ENV 123\n")
        f.write("EXEC_ENV NOT_SET")

    ext_job = ExtJob("EXEC_ENV", False)
    job_list = ExtJoblist()
    job_list.add_job("EXEC_ENV", ext_job)
    forward_model = ForwardModel(job_list)
    forward_model.add_job("EXEC_ENV")
    global_args = SubstitutionList()
    env_varlist = EnvironmentVarlist()
    forward_model.formatted_fprintf(
        "run_id", None, "data_root", global_args, 0, env_varlist
    )

    with open("jobs.json", "r") as f:
        jobs_json = json.load(f)

    for msg in list(JobRunner(jobs_json).run([])):
        if isinstance(msg, Start):
            with open("exec_env_exec_env.json") as f:
                exec_env = json.load(f)
                assert exec_env["TEST_ENV"] == "123"
                assert exec_env["NOT_SET"] is None
