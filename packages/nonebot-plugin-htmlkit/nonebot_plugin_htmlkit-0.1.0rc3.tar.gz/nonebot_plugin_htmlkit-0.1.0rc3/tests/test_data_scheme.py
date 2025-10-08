from pathlib import Path

import aiofiles
import pytest
from utils import assert_image_equal

DATA_SCHEME_PATH = Path(__file__).parent / "data_scheme"

HTML_SOURCES = [
    name.stem for name in DATA_SCHEME_PATH.iterdir() if name.suffix == ".html"
]

NATIVE = [True]

FORMATS = ["png", "jpeg"]


@pytest.mark.asyncio
@pytest.mark.parametrize("image_format", FORMATS)
@pytest.mark.parametrize("native", NATIVE)
@pytest.mark.parametrize("html_name", HTML_SOURCES)
async def test_render_image_from_data_scheme(
    html_name, image_format, regen_ref, output_img_dir, native
):
    from nonebot_plugin_htmlkit import (
        combined_css_fetcher,
        combined_img_fetcher,
        html_to_pic,
        none_fetcher,
    )

    html_path = DATA_SCHEME_PATH / f"{html_name}.html"
    async with aiofiles.open(html_path, encoding="utf-8") as f:
        html_src = await f.read()

    img_bytes = await html_to_pic(
        html_src,
        max_width=2560,
        allow_refit=True,
        image_format=image_format,
        native_data_scheme=native,
        css_fetch_fn=none_fetcher if native else combined_css_fetcher,
        img_fetch_fn=none_fetcher if native else combined_img_fetcher,
    )
    assert img_bytes.startswith(
        b"\x89PNG\r\n\x1a\n" if image_format == "png" else b"\xff\xd8"
    )

    filename = f"data_scheme_{html_name}{'_native' if native else ''}.{image_format}"
    await assert_image_equal(img_bytes, filename, regen_ref, output_img_dir)
