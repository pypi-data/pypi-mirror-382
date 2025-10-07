import pytest
from bluer_objects.README.consts import (
    assets_path,
    asset_volume,
    designs_repo,
    designs_url,
)


@pytest.mark.parametrize(
    ["suffix"],
    [
        ["this"],
        ["that/which"],
    ],
)
@pytest.mark.parametrize(
    ["volume"],
    [
        [""],
        ["2"],
        [2],
    ],
)
def test_README_assets(
    suffix: str,
    volume: str,
):
    volume_path = asset_volume(volume=volume)
    assert isinstance(volume_path, str)
    assert volume_path.endswith(volume_path)

    path = assets_path(
        suffix=suffix,
        volume=volume,
    )

    assert isinstance(path, str)
    assert path.endswith(suffix)
    assert volume_path in path


@pytest.mark.parametrize(
    ["suffix"],
    [
        ["this"],
        ["that/which"],
    ],
)
def test_README_designs_url(suffix):
    url = designs_url(suffix=suffix)

    assert isinstance(url, str)
    assert url.startswith(designs_repo)
    assert url.endswith(suffix)
