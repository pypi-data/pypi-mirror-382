import re
import pytest
from ewokstomo.tasks import dataportalupload
from ewokscore.missing_data import MissingData

PROCESSED = "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA/sample/sample_dataset"
RAW = "/data/visitor/ma0000/id00/20250101/RAW_DATA/sample/sample_dataset"


def make_task(inputs: dict):
    return dataportalupload.DataPortalUpload(inputs=inputs)


def _last_dryrun_message(caplog) -> str | None:
    msgs = [r.message for r in caplog.records if r.levelname == "INFO"]
    for m in reversed(msgs):
        if "Dry-run: would store_processed_data" in m:
            return m
    return None


def test_dry_run_happy_case_logs_basic_fields(caplog):
    t = make_task(
        {
            "process_folder_path": PROCESSED,
            "metadata": {"Sample_name": "override_sample", "extra": 42},
            "dry_run": True,
        }
    )
    with caplog.at_level("INFO"):
        t.run()

    msg = _last_dryrun_message(caplog)
    assert msg, "Expected dry-run log line not found"
    assert "proposal=ma0000" in msg
    assert "beamline=id00" in msg
    assert "dataset=dataset" in msg
    assert f"path={PROCESSED}" in msg
    assert f"raw=['{RAW}']" in msg


def test_dry_run_infers_sample_name_is_mentioned(caplog):
    t = make_task(
        {
            "process_folder_path": PROCESSED,
            "metadata": MissingData(),
            "dry_run": True,
        }
    )
    with caplog.at_level("INFO"):
        t.run()

    msg = _last_dryrun_message(caplog)
    assert msg, "Expected dry-run log line not found"
    assert "Sample_name" in msg
    assert "sample" in msg


def test_dry_run_adds_missing_sample_key_is_mentioned(caplog):
    t = make_task(
        {
            "process_folder_path": PROCESSED,
            "metadata": {"foo": "bar"},
            "dry_run": True,
        }
    )
    with caplog.at_level("INFO"):
        t.run()

    msg = _last_dryrun_message(caplog)
    assert msg, "Expected dry-run log line not found"
    assert "foo" in msg and "bar" in msg
    assert "Sample_name" in msg and "sample" in msg


STRUCTURE_REGEX = re.compile(
    r"Expected\s+PROCESSED_DATA/<sample>/<(?:sample_)?dataset>(?:\s+path\s+structure\.)?",
    re.I,
)
FALLBACK_PATTERNS = [
    re.compile(r"Field has no value:\s*'(dataset|collection)'", re.I),
    re.compile(r"missing\s+value.*(dataset|collection)", re.I),
    re.compile(r"\b(dataset|collection)\b.*(missing|none|null|empty)", re.I),
    re.compile(r"(missing|required).*(dataset|collection)", re.I),
]


@pytest.mark.parametrize(
    "bad_path, preferred_pattern",
    [
        (
            "/data/visitor/ma0000/id00/20250101/RAW_DATA/sample/sample_dataset",
            re.compile(r"Not a\s+PROCESSED_DATA\s+path", re.I),
        ),
        (
            "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA",
            STRUCTURE_REGEX,
        ),
        (
            "/data/visitor/ma0000/id00/20250101/PROCESSED_DATA/sample_only",
            STRUCTURE_REGEX,
        ),
    ],
)
def test_validation_errors_log_warning_and_no_dryrun(
    caplog, bad_path, preferred_pattern
):
    t = make_task(
        {
            "process_folder_path": bad_path,
            "metadata": MissingData(),
            "dry_run": True,
        }
    )
    with caplog.at_level("WARNING"):
        t.run()

    warnings = [r.message or "" for r in caplog.records if r.levelname == "WARNING"]

    matched = any(preferred_pattern.search(m) for m in warnings) or any(
        p.search(m) for p in FALLBACK_PATTERNS for m in warnings
    )

    assert matched, (
        "No WARNING matched preferred or fallback patterns.\n"
        f"Preferred: {preferred_pattern.pattern}\n"
        "Warnings were:\n- " + "\n- ".join(warnings)
    )

    assert _last_dryrun_message(caplog) is None
