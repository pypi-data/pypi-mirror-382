from typing import Union

github_kamangir = "https://github.com/kamangir"
designs_repo = f"{github_kamangir}/designs/"


def designs_url(suffix: str) -> str:
    return f"{designs_repo}/blob/main/{suffix}"


def asset_volume(volume: Union[str, int] = "") -> str:
    return f"{github_kamangir}/assets{str(volume)}/raw/main"


assets = asset_volume(volume="")
assets2 = asset_volume(volume="2")


def assets_path(
    suffix: str,
    volume: Union[str, int] = "",
) -> str:
    return "{}/{}".format(
        asset_volume(volume=volume),
        suffix,
    )
