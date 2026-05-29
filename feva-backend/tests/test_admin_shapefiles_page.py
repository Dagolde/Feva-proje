"""Tests for admin shapefile management page.

Requirements: 7.1, 7.4, 7.5
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_admin_shapefiles_page_requires_admin_role(async_client: AsyncClient, qa_token: str):
    """Test that shapefile management page requires admin role."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": qa_token}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_shapefiles_page_accessible_to_admin(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page is accessible to admin users."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "Shapefile Management" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_upload_form(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page has upload form."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "uploadForm" in response.text
    assert "layerName" in response.text
    assert "versionTag" in response.text
    assert "shapefileZip" in response.text
    assert "Upload Shapefile" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_version_table(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page contains version history table."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "shapefilesTable" in response.text
    assert "<thead>" in response.text
    assert "Layer Name" in response.text
    assert "Version Tag" in response.text
    assert "Uploaded By" in response.text
    assert "Uploaded At" in response.text
    assert "Status" in response.text
    assert "Checksum" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_file_validation(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page includes file validation."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check for file size validation (50MB)
    assert "50MB" in response.text or "50 MB" in response.text
    # Check for ZIP file requirement
    assert ".zip" in response.text.lower()


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_upload_progress(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page has upload progress indicator."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "uploadProgress" in response.text
    assert "progressBar" in response.text
    assert "uploadStatus" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_activate_modal(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page has activation modal."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "activateModal" in response.text
    assert "Activate Shapefile Version" in response.text
    assert "activateShapefileId" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_activation_controls(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page has activation controls."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "openActivateModal" in response.text or "Activate" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_displays_checksum(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page displays SHA-256 checksum."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "checksum" in response.text.lower()
    assert "copyToClipboard" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_loads_common_js(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page loads common.js utilities."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "/static/js/common.js" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_redirects_unauthenticated(async_client: AsyncClient):
    """Test that unauthenticated users are redirected to login."""
    response = await async_client.get("/admin/shapefiles", follow_redirects=False)
    assert response.status_code in [302, 307]
    assert "login" in response.headers.get("location", "").lower()


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_responsive_design(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page includes responsive design elements."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check for responsive CSS media queries
    assert "@media" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_uses_api_endpoints(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page uses the correct API endpoints."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check that JavaScript references the correct API endpoints
    assert "/api/v1/admin/shapefiles" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_refresh_button(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page has refresh functionality."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "loadShapefiles" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_shows_active_status(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page displays active/inactive status."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "is_active" in response.text or "Active" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_layer_name_input(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page has layer name input with examples."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "Layer Name" in response.text
    # Check for example layer names
    assert "lga" in response.text.lower() or "ward" in response.text.lower()


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_version_tag_input(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page has version tag input with examples."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    assert "Version Tag" in response.text
    # Check for example version format
    assert "2025" in response.text or "Q1" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_handles_empty_state(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page handles empty state gracefully."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check for empty state message
    assert "No shapefile versions found" in response.text or "Upload your first shapefile" in response.text


@pytest.mark.asyncio
async def test_admin_shapefiles_page_has_form_validation_messages(async_client: AsyncClient, admin_token: str):
    """Test that shapefile management page includes validation messages."""
    response = await async_client.get(
        "/admin/shapefiles",
        cookies={"access_token": admin_token}
    )
    assert response.status_code == 200
    # Check for validation logic in JavaScript
    assert "required" in response.text.lower()
    assert "validate" in response.text.lower() or "validation" in response.text.lower()
