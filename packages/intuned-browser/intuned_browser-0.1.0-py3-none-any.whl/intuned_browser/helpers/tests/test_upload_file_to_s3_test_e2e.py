import os

import pytest
from dotenv import load_dotenv
from runtime import launch_chromium
from runtime.context.context import IntunedContext
from runtime.types.run_types import IntunedRunContext

from intuned_browser import download_file
from intuned_browser import save_file_to_s3
from intuned_browser import upload_file_to_s3

load_dotenv(override=True)


os.environ["MODE"] = ""


@pytest.mark.asyncio
@pytest.mark.headed
@pytest.mark.skip
async def test_upload_file_to_s3():
    with IntunedContext() as ctx:
        ctx.run_context = IntunedRunContext(
            job_id="sample-job",
            job_run_id="eb722252-e932-4658-ac35-c846ed5b4f44",
            run_id="yyPCx2XF7Eu9nda",
            auth_session_id=None,
        )
        async with launch_chromium(headless=False) as (context, page):
            await page.goto("https://sandbox.intuned.dev/pdfs")

            download = await download_file(
                page,
                "https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2",
            )

            uploaded_file = await upload_file_to_s3(download)
            print(uploaded_file.suggested_file_name)

            saved_file_to_s3 = await save_file_to_s3(
                page=page,
                trigger="https://cdn11.bigcommerce.com/s-scmrv6kkrz/images/stencil/1280x1280/products/192719/166712/1891-clear-14-vdc-miniature-lb93__16581.1568390384.jpg?c=2",
            )
            await saved_file_to_s3.get_signed_url()

            signed_url = await uploaded_file.get_signed_url()
            print(signed_url)
            assert signed_url is not None
            assert signed_url.startswith("https://")
            assert uploaded_file.file_name is not None


@pytest.mark.asyncio
@pytest.mark.headed
async def test_download_url():
    async with launch_chromium(headless=False) as (context, page):
        await page.goto("https://sandbox.intuned.dev/pdfs")

        download = await download_file(
            page,
            "https://intuned-docs-public-images.s3.amazonaws.com/27UP600_27UP650_ENG_US.pdf",
        )
        assert download is not None


@pytest.mark.asyncio
@pytest.mark.headed
async def test_download_locator():
    async with launch_chromium(headless=False) as (context, page):
        await page.goto("https://sandbox.intuned.dev/pdfs")

        download = await download_file(
            page,
            lambda page: page.locator("xpath=/html/body/div/div/main/div/div/div/table/tbody/tr[1]/td[4]/a").click(),
        )
        assert download is not None
