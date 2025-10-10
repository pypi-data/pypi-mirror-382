from pathlib import Path

import pytest
import respx
from httpx import ReadTimeout, Response
from typer.testing import CliRunner

from fastapi_cloud_cli.cli import app
from fastapi_cloud_cli.config import Settings

runner = CliRunner()
settings = Settings.get()

assets_path = Path(__file__).parent / "assets"


@pytest.mark.respx(base_url=settings.base_api_url)
def test_shows_a_message_if_something_is_wrong(
    logged_in_cli: None, respx_mock: respx.MockRouter
) -> None:
    respx_mock.get("/users/me").mock(return_value=Response(500))

    result = runner.invoke(app, ["whoami"])

    assert (
        "Something went wrong while contacting the FastAPI Cloud server."
        in result.output
    )
    assert result.exit_code == 1


@pytest.mark.respx(base_url=settings.base_api_url)
def test_shows_a_message_when_token_is_invalid(
    logged_in_cli: None, respx_mock: respx.MockRouter
) -> None:
    respx_mock.get("/users/me").mock(return_value=Response(401))

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 1
    assert "The specified token is not valid" in result.output


@pytest.mark.respx(base_url=settings.base_api_url)
def test_shows_email(logged_in_cli: None, respx_mock: respx.MockRouter) -> None:
    respx_mock.get("/users/me").mock(
        return_value=Response(200, json={"email": "email@fastapi.com"})
    )

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 0
    assert "email@fastapi.com" in result.output


@pytest.mark.respx(base_url=settings.base_api_url)
def test_handles_read_timeout(
    logged_in_cli: None, respx_mock: respx.MockRouter
) -> None:
    respx_mock.get("/users/me").mock(side_effect=ReadTimeout)

    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 1
    assert "The request to the FastAPI Cloud server timed out" in result.output


def test_prints_not_logged_in(logged_out_cli: None) -> None:
    result = runner.invoke(app, ["whoami"])

    assert result.exit_code == 0
    assert "No credentials found. Use `fastapi login` to login." in result.output
