import pytest

from azpipeline import AzurePipeline


def test_build_id() -> None:
    with pytest.raises(SystemExit) as e:
        AzurePipeline(build_id="")
    assert e.type == SystemExit
    assert e.value.code == 1
