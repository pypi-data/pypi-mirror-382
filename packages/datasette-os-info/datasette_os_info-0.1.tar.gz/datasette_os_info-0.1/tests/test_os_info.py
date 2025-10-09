from datasette.app import Datasette
import pytest


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-os-info" in installed_plugins


@pytest.mark.asyncio
async def test_os_endpoint():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/os")
    assert response.status_code == 200
    data = response.json()

    # Check that basic platform info is present
    assert "platform" in data
    assert "system" in data["platform"]
    assert "release" in data["platform"]
    assert "python_version" in data["platform"]

    # Check that hostname is present
    assert "hostname" in data

    # Check that cpu_count is present
    assert "cpu_count" in data

    # Check that python_executable is present
    assert "python_executable" in data
