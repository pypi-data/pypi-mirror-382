from ctapipe.core import run_tool

from lstcam_calib.conftest import (
    TEST_ONSITE,
    test_data,
    test_drs4_pedestal_file,
    test_drs4_pedestal_provenance_log,
)
from lstcam_calib.io.database import CalibrationType
from lstcam_calib.tools.change_database_document import (
    ChangeDataBaseDocument,
    ChangeType,
)


def test_change_database_document(onsite_test_tree, onsite_database):
    """Test validate_calibration_file tool."""
    drs4_pedestal_file = (
        onsite_test_tree
        / test_drs4_pedestal_file.resolve().relative_to(test_data / "real")
    )

    drs4_pedestal_file_provence_log = (
        onsite_test_tree
        / test_drs4_pedestal_provenance_log.resolve().relative_to(test_data / "real")
    )

    # disable and invalidate document
    changes_to_test = [ChangeType.disable, ChangeType.invalidate]

    for change in changes_to_test:
        ret = run_tool(
            ChangeDataBaseDocument(),
            argv=[
                f"--base-dir={onsite_test_tree}",
                f"--type={CalibrationType.DRS4_BASELINE.name}",
                f"--input={drs4_pedestal_file}",
                f"--change={change}",
                f"--db-name={TEST_ONSITE}",
                "--yes",
            ],
            cwd=onsite_test_tree,
        )
        assert ret == 0

    # test remove
    ret = run_tool(
        ChangeDataBaseDocument(),
        argv=[
            f"--base-dir={onsite_test_tree}",
            f"--type={CalibrationType.DRS4_BASELINE.name}",
            f"--input={drs4_pedestal_file}",
            f"--change={ChangeType.remove}",
            f"--db-name={TEST_ONSITE}",
            "--yes",
        ],
        cwd=onsite_test_tree,
    )
    assert ret == 0

    # add it again
    run = 2005

    onsite_database.add_drs4_baseline_file(
        path=drs4_pedestal_file,
        provenance_path=drs4_pedestal_file_provence_log,
        obs_id=run,
        local_run_id=run,
    )
    # validate and enable document
    changes_to_test = [
        ChangeType.validate,
        ChangeType.enable,
    ]

    for change in changes_to_test:
        ret = run_tool(
            ChangeDataBaseDocument(),
            argv=[
                f"--base-dir={onsite_test_tree}",
                f"--type={CalibrationType.DRS4_BASELINE.name}",
                f"--input={drs4_pedestal_file}",
                f"--change={change}",
                f"--db-name={TEST_ONSITE}",
                "--yes",
            ],
            cwd=onsite_test_tree,
        )
        assert ret == 0
