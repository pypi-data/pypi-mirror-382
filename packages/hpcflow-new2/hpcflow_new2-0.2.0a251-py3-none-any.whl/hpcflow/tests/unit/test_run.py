from __future__ import annotations

import os

import pytest

from pathlib import Path
from hpcflow.app import app as hf
from hpcflow.sdk.core.actions import SkipReason
from hpcflow.sdk.core.test_utils import make_workflow_to_run_command


def test_compose_commands_no_shell_var(null_config, tmp_path: Path):
    ts = hf.TaskSchema(
        objective="test_compose_commands",
        actions=[hf.Action(commands=[hf.Command(command="Start-Sleep 10")])],
    )
    wk = hf.Workflow.from_template_data(
        template_name="test_compose_commands",
        path=tmp_path,
        tasks=[hf.Task(schema=ts)],
    )
    sub = wk.add_submission()
    assert sub is not None
    js = sub.jobscripts[0]
    run = wk.tasks[0].elements[0].iterations[0].action_runs[0]
    _, shell_vars = run.compose_commands(environments=sub.environments, shell=js.shell)
    assert shell_vars == {0: []}


def test_compose_commands_single_shell_var(null_config, tmp_path: Path):
    ts = hf.TaskSchema(
        objective="test_compose_commands",
        inputs=[hf.SchemaInput("p1")],
        outputs=[hf.SchemaOutput("p1")],
        actions=[
            hf.Action(
                commands=[
                    hf.Command(
                        command="Write-Output (<<parameter:p1>> + 100)",
                        stdout="<<int(parameter:p1)>>",
                    ),
                ],
            ),
        ],
    )
    wk = hf.Workflow.from_template_data(
        template_name="test_compose_commands",
        path=tmp_path,
        tasks=[hf.Task(schema=ts, inputs={"p1": 101})],
    )
    sub = wk.add_submission()
    assert sub is not None
    js = sub.jobscripts[0]
    run = wk.tasks[0].elements[0].iterations[0].action_runs[0]
    _, shell_vars = run.compose_commands(environments=sub.environments, shell=js.shell)
    assert shell_vars == {0: [("outputs.p1", "parameter_p1", "stdout")]}


def test_compose_commands_multi_single_shell_var(null_config, tmp_path: Path):
    ts = hf.TaskSchema(
        objective="test_compose_commands",
        inputs=[hf.SchemaInput("p1")],
        outputs=[hf.SchemaOutput("p1")],
        actions=[
            hf.Action(
                commands=[
                    hf.Command(command="Start-Sleep 10"),
                    hf.Command(
                        command="Write-Output (<<parameter:p1>> + 100)",
                        stdout="<<int(parameter:p1)>>",
                    ),
                ],
            ),
        ],
    )
    wk = hf.Workflow.from_template_data(
        template_name="test_compose_commands",
        path=tmp_path,
        tasks=[hf.Task(schema=ts, inputs={"p1": 101})],
    )
    sub = wk.add_submission()
    assert sub is not None
    js = sub.jobscripts[0]
    run = wk.tasks[0].elements[0].iterations[0].action_runs[0]
    _, shell_vars = run.compose_commands(environments=sub.environments, shell=js.shell)
    assert shell_vars == {0: [], 1: [("outputs.p1", "parameter_p1", "stdout")]}


@pytest.mark.integration
def test_run_dir_diff_new_file(null_config, tmp_path):
    if os.name == "nt":
        command = "New-Item -Path 'new_file.txt' -ItemType File"
    else:
        command = "touch new_file.txt"
    wk = make_workflow_to_run_command(
        command=command,
        requires_dir=True,
        path=tmp_path,
        name="w2",
        overwrite=True,
    )
    wk.submit(wait=True, add_to_known=False, status=False)
    assert wk.get_all_EARs()[0].dir_diff.files_created == ["new_file.txt"]


@pytest.mark.integration
def test_run_skip_reason_upstream_failure(null_config, tmp_path):
    ts = hf.TaskSchema(
        objective="t1",
        inputs=[hf.SchemaInput("p1")],
        outputs=[hf.SchemaInput("p2")],
        actions=[
            hf.Action(
                commands=[
                    hf.Command(
                        command="echo $(( <<parameter:p1>> + 100 ))",
                        stdout="<<parameter:p2>>",
                    ),
                    hf.Command(command="exit 1"),
                ]
            ),
            hf.Action(
                commands=[
                    hf.Command(
                        command="echo $(( <<parameter:p2>> + 100 ))",
                        stdout="<<parameter:p2>>",
                    ),
                ]
            ),  # should be skipped due to failure of action 0
        ],
    )
    wk = hf.Workflow.from_template_data(
        template_name="test_skip_reason",
        path=tmp_path,
        tasks=[hf.Task(schema=ts, inputs={"p1": 100})],
    )
    wk.submit(wait=True, add_to_known=False, status=False)
    runs = wk.get_all_EARs()
    assert not runs[0].success
    assert not runs[1].success
    assert runs[0].skip_reason is SkipReason.NOT_SKIPPED
    assert runs[1].skip_reason is SkipReason.UPSTREAM_FAILURE


@pytest.mark.integration
def test_run_skip_reason_loop_termination(null_config, tmp_path):
    ts = hf.TaskSchema(
        objective="t1",
        inputs=[hf.SchemaInput("p1")],
        outputs=[hf.SchemaInput("p1")],
        actions=[
            hf.Action(
                commands=[
                    hf.Command(
                        command="echo $(( <<parameter:p1>> + 100 ))",
                        stdout="<<int(parameter:p1)>>",
                    ),
                ]
            ),
        ],
    )
    loop_term = hf.Rule(path="outputs.p1", condition={"value.equal_to": 300})
    wk = hf.Workflow.from_template_data(
        template_name="test_skip_reason",
        path=tmp_path,
        tasks=[hf.Task(schema=ts, inputs={"p1": 100})],
        loops=[
            hf.Loop(name="my_loop", tasks=[0], termination=loop_term, num_iterations=3)
        ],
    )
    # loop should terminate after the second iteration
    wk.submit(wait=True, add_to_known=False, status=False)
    runs = wk.get_all_EARs()

    assert runs[0].get("outputs.p1") == 200
    assert runs[1].get("outputs.p1") == 300
    assert not runs[2].get("outputs.p1")

    assert runs[0].success
    assert runs[1].success
    assert not runs[2].success

    assert runs[0].skip_reason is SkipReason.NOT_SKIPPED
    assert runs[1].skip_reason is SkipReason.NOT_SKIPPED
    assert runs[2].skip_reason is SkipReason.LOOP_TERMINATION


def test_get_data_in_values_input_files(null_config, tmp_path: Path):
    with (file_name := Path("my_file.txt")).open("wt") as fh:
        fh.write("hello!\n")
    file_spec = hf.FileSpec("my_file", str(file_name))
    s1 = hf.TaskSchema(
        objective="t1",
        inputs=[
            hf.SchemaInput(parameter="p1"),
        ],
        actions=[
            hf.Action(
                input_file_generators=[
                    hf.InputFileGenerator(
                        input_file=file_spec,
                        inputs=[hf.Parameter("p1")],
                    )
                ],
            )
        ],
    )
    t1 = hf.Task(schema=[s1], input_files=[hf.InputFile(file_spec, path="my_file.txt")])
    wk = hf.Workflow.from_template_data(
        tasks=[t1],
        path=tmp_path,
        template_name="test_get_data_in_values_input_files",
    )
    run = wk.tasks[0].elements[0].iterations[0].action_runs[0]
    assert run.get_data_in_values(("input_files.my_file",)) == {
        "my_file": wk.input_files_path.joinpath("0/my_file.txt").as_posix()
    }


def test_get_data_in_values_user_provided_input_file(null_config, tmp_path: Path):

    # pass an input file so the IFG doesn't need to run
    with (file_name := Path("my_file.txt")).open("wt") as fh:
        fh.write("hello!\n")

    file_spec = hf.FileSpec("my_file", str(file_name))
    s1 = hf.TaskSchema(
        objective="t1",
        inputs=[
            hf.SchemaInput(parameter="p1"),
        ],
        actions=[
            hf.Action(
                input_file_generators=[
                    hf.InputFileGenerator(
                        input_file=file_spec,
                        inputs=[hf.Parameter("p1")],
                    )
                ],
            )
        ],
    )
    t1 = hf.Task(schema=[s1], input_files=[hf.InputFile(file_spec, path="my_file.txt")])
    wk = hf.Workflow.from_template_data(
        tasks=[t1],
        path=tmp_path,
        template_name="test_get_data_in_values_input_files",
    )
    run = wk.tasks[0].elements[0].iterations[0].action_runs[0]
    assert run.get_data_in_values(("input_files.my_file",)) == {
        "my_file": wk.input_files_path.joinpath("0/my_file.txt").as_posix()
    }


def test_get_data_in_values_input_file_to_script(null_config, tmp_path: Path):
    # pass an input file so the IFG doesn't need to run
    with (file_name := Path("my_file.txt")).open("wt") as fh:
        fh.write("hello!\n")

    file_spec = hf.FileSpec("my_file", str(file_name))
    act = hf.Action(
        input_file_generators=[
            hf.InputFileGenerator(
                input_file=file_spec,
                inputs=[hf.Parameter("p1")],
            )
        ],
        script_data_in={"input_files.my_file": "direct"},
    )
    s1 = hf.TaskSchema(
        objective="ts1",
        inputs=[hf.SchemaInput("p1")],
        actions=[act],
    )
    t1 = hf.Task(schema=[s1], input_files=[hf.InputFile(file_spec, path="my_file.txt")])
    wk = hf.Workflow.from_template_data(
        tasks=[t1],
        path=tmp_path,
        template_name="test_get_data_in_values_input_files",
    )
    act_runs = wk.tasks[0].elements[0].iterations[0].action_runs
    assert len(act_runs) == 1
    assert act_runs[0].get_data_in_values(("input_files.my_file",)) == {
        "my_file": wk.input_files_path.joinpath("0/my_file.txt").as_posix()
    }
