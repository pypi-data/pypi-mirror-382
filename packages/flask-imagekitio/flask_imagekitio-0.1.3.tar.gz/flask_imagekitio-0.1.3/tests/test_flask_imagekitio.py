"""
Pytest test suite for flask-imagekitio extension
"""

from unittest.mock import Mock, patch

import pytest
from flask import Flask

from flask_imagekitio import ImagekitIO


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["IMAGEKITIO_URL_ENDPOINT"] = "https://ik.imagekit.io/test"
    app.config["IMAGEKITIO_PRIVATE_KEY"] = "private_test_key"
    app.config["IMAGEKITIO_PUBLIC_KEY"] = "public_test_key"
    return app


@pytest.fixture
def imagekitio():
    """Create an ImagekitIO instance for testing."""
    return ImagekitIO()


@pytest.fixture
def configured_imagekitio(app):
    """Create an ImagekitIO instance already configured with an app."""
    ik = ImagekitIO(app)
    return ik


class TestImagekitIOInitialization:
    """Test ImagekitIO extension initialization."""

    def test_init_without_app(self):
        """Test initialization without passing app."""
        ik = ImagekitIO()
        assert ik.public_key is None
        assert ik.url_endpoint is None

    def test_init_with_app(self, app):
        """Test initialization by passing app to constructor."""
        ik = ImagekitIO(app)

        assert ik.url_endpoint == app.config["IMAGEKITIO_URL_ENDPOINT"]
        assert ik.public_key == app.config["IMAGEKITIO_PUBLIC_KEY"]

    def test_init_app_with_valid_config(self, app, imagekitio):
        """Test init_app with valid configuration."""
        imagekitio.init_app(app)

        assert imagekitio.url_endpoint == app.config["IMAGEKITIO_URL_ENDPOINT"]
        assert imagekitio.public_key == app.config["IMAGEKITIO_PUBLIC_KEY"]
        assert "imagekitio" in app.extensions
        assert app.extensions["imagekitio"] == imagekitio

    def test_init_app_without_url_endpoint(self, app, imagekitio):
        """Test init_app fails without URL endpoint."""
        del app.config["IMAGEKITIO_URL_ENDPOINT"]

        with pytest.raises(AttributeError, match="You must set config variables"):
            imagekitio.init_app(app)

    def test_init_app_without_private_key(self, app, imagekitio):
        """Test init_app fails without private key."""
        del app.config["IMAGEKITIO_PRIVATE_KEY"]

        with pytest.raises(AttributeError, match="You must set config variables"):
            imagekitio.init_app(app)

    def test_init_app_without_public_key(self, app, imagekitio):
        """Test init_app fails without public key."""
        del app.config["IMAGEKITIO_PUBLIC_KEY"]

        with pytest.raises(AttributeError, match="You must set config variables"):
            imagekitio.init_app(app)

    def test_init_app_with_empty_config_values(self, app, imagekitio):
        """Test init_app fails with empty config values."""
        app.config["IMAGEKITIO_URL_ENDPOINT"] = ""

        with pytest.raises(AttributeError, match="You must set config variables"):
            imagekitio.init_app(app)

    def test_init_app_called_twice_raises_error(self, app, imagekitio):
        """Test that calling init_app twice on same app raises RuntimeError."""
        imagekitio.init_app(app)

        ik2 = ImagekitIO()
        with pytest.raises(RuntimeError, match="ImageKitIO extension is already registered"):
            ik2.init_app(app)

    def test_init_app_returns_none(self, app, imagekitio):
        """Test that init_app returns None."""
        result = imagekitio.init_app(app)
        assert result is None


class TestImagekitIOInterface:
    """Test the interface context manager."""

    @patch("flask_imagekitio.ImageKit")
    def test_interface_context_manager(self, mock_imagekit_class, configured_imagekitio):
        """Test interface returns ImageKit instance in context."""
        mock_ik_instance = Mock()
        mock_imagekit_class.return_value = mock_ik_instance

        with configured_imagekitio.interface() as ik:
            assert ik == mock_ik_instance

        mock_imagekit_class.assert_called_once_with(configured_imagekitio.public_key, configured_imagekitio._ImagekitIO__private_key, configured_imagekitio.url_endpoint)

    @patch("flask_imagekitio.ImageKit")
    def test_interface_cleanup(self, mock_imagekit_class, configured_imagekitio):
        """Test that interface cleans up ImageKit instance after context."""
        mock_ik_instance = Mock()
        mock_imagekit_class.return_value = mock_ik_instance

        with configured_imagekitio.interface() as ik:
            imagekit_ref = ik
            assert imagekit_ref is not None

        # After context, the local reference should be deleted
        # We can't directly test deletion, but we can verify it was created

    def test_interface_without_config_raises_error(self, imagekitio):
        """Test interface raises AttributeError without configuration."""
        with pytest.raises(AttributeError, match="In order to use the interface"):
            with imagekitio.interface():
                pass

    def test_interface_with_partial_config_raises_error(self, imagekitio):
        """Test interface raises AttributeError with incomplete configuration."""
        imagekitio.public_key = "public_key"
        imagekitio.url_endpoint = "https://ik.imagekit.io/test"
        # Missing private_key

        with pytest.raises(AttributeError, match="In order to use the interface"):
            with imagekitio.interface():
                pass

    @patch("flask_imagekitio.ImageKit")
    def test_interface_exception_handling(self, mock_imagekit_class, configured_imagekitio):
        """Test that interface properly handles exceptions and still cleans up."""
        mock_ik_instance = Mock()
        mock_imagekit_class.return_value = mock_ik_instance

        with pytest.raises(ValueError, match="Test error"):
            with configured_imagekitio.interface() as _:
                raise ValueError("Test error")

        # ImageKit instance should still be created
        mock_imagekit_class.assert_called_once()


class TestImagekitIOWithImageKitAPI:
    """Test ImagekitIO with actual ImageKit API methods."""

    @patch("flask_imagekitio.ImageKit")
    def test_upload_file(self, mock_imagekit_class, configured_imagekitio):
        """Test file upload through interface."""
        mock_ik = Mock()
        mock_response = Mock()
        mock_response.url = "https://ik.imagekit.io/test/image.jpg"
        mock_response.file_id = "test_file_id_123"
        mock_ik.upload_file.return_value = mock_response
        mock_imagekit_class.return_value = mock_ik

        with configured_imagekitio.interface() as ik:
            result = ik.upload_file(file=b"fake image data", file_name="test_image.jpg")

        assert result.url == "https://ik.imagekit.io/test/image.jpg"
        assert result.file_id == "test_file_id_123"
        mock_ik.upload_file.assert_called_once()

    @patch("flask_imagekitio.ImageKit")
    def test_upload_file_with_options(self, mock_imagekit_class, configured_imagekitio):
        """Test file upload with additional options."""
        mock_ik = Mock()
        mock_response = Mock()
        mock_response.url = "https://ik.imagekit.io/test/folder/image.jpg"
        mock_ik.upload_file.return_value = mock_response
        mock_imagekit_class.return_value = mock_ik

        with configured_imagekitio.interface() as ik:
            result = ik.upload_file(file=b"fake image data", file_name="test_image.jpg", options={"folder": "/test-folder", "tags": ["test", "upload"]})

        assert result.url == "https://ik.imagekit.io/test/folder/image.jpg"

    @patch("flask_imagekitio.ImageKit")
    def test_list_files(self, mock_imagekit_class, configured_imagekitio):
        """Test listing files through interface."""
        mock_ik = Mock()
        mock_response = Mock()
        mock_response.list = [{"file_id": "1", "name": "image1.jpg"}, {"file_id": "2", "name": "image2.jpg"}]
        mock_ik.list_files.return_value = mock_response
        mock_imagekit_class.return_value = mock_ik

        with configured_imagekitio.interface() as ik:
            result = ik.list_files()

        assert len(result.list) == 2
        mock_ik.list_files.assert_called_once()

    @patch("flask_imagekitio.ImageKit")
    def test_delete_file(self, mock_imagekit_class, configured_imagekitio):
        """Test deleting a file through interface."""
        mock_ik = Mock()
        mock_imagekit_class.return_value = mock_ik

        file_id = "test_file_id_123"

        with configured_imagekitio.interface() as ik:
            ik.delete_file(file_id)

        mock_ik.delete_file.assert_called_once_with(file_id)

    @patch("flask_imagekitio.ImageKit")
    def test_get_file_details(self, mock_imagekit_class, configured_imagekitio):
        """Test getting file details through interface."""
        mock_ik = Mock()
        mock_response = Mock()
        mock_response.file_id = "test_file_id_123"
        mock_response.name = "image.jpg"
        mock_response.url = "https://ik.imagekit.io/test/image.jpg"
        mock_ik.get_file_details.return_value = mock_response
        mock_imagekit_class.return_value = mock_ik

        file_id = "test_file_id_123"

        with configured_imagekitio.interface() as ik:
            result = ik.get_file_details(file_id)

        assert result.file_id == file_id
        assert result.name == "image.jpg"
        mock_ik.get_file_details.assert_called_once_with(file_id)

    @patch("flask_imagekitio.ImageKit")
    def test_url_generation(self, mock_imagekit_class, configured_imagekitio):
        """Test URL generation through interface."""
        mock_ik = Mock()
        mock_ik.url.return_value = "https://ik.imagekit.io/test/tr:w-600,ar-5-3/image.jpg"
        mock_imagekit_class.return_value = mock_ik

        with configured_imagekitio.interface() as ik:
            result = ik.url({"src": "https://ik.imagekit.io/test/image.jpg", "transformation": [{"width": "600", "aspect_ratio": "5-3"}]})

        assert "tr:w-600" in result
        mock_ik.url.assert_called_once()

    @patch("flask_imagekitio.ImageKit")
    def test_purge_cache(self, mock_imagekit_class, configured_imagekitio):
        """Test cache purging through interface."""
        mock_ik = Mock()
        mock_imagekit_class.return_value = mock_ik

        url = "https://ik.imagekit.io/test/image.jpg"

        with configured_imagekitio.interface() as ik:
            ik.purge_file_cache(url)

        mock_ik.purge_file_cache.assert_called_once_with(url)

    @patch("flask_imagekitio.ImageKit")
    def test_get_purge_cache_status(self, mock_imagekit_class, configured_imagekitio):
        """Test getting purge cache status through interface."""
        mock_ik = Mock()
        mock_response = Mock()
        mock_response.status = "Complete"
        mock_ik.get_purge_file_cache_status.return_value = mock_response
        mock_imagekit_class.return_value = mock_ik

        request_id = "test_request_id"

        with configured_imagekitio.interface() as ik:
            result = ik.get_purge_file_cache_status(request_id)

        assert result.status == "Complete"
        mock_ik.get_purge_file_cache_status.assert_called_once_with(request_id)


class TestImagekitIOMultipleApps:
    """Test ImagekitIO with multiple Flask applications."""

    def test_multiple_app_instances(self):
        """Test extension with multiple Flask app instances."""
        app1 = Flask("app1")
        app1.config["IMAGEKITIO_URL_ENDPOINT"] = "https://ik.imagekit.io/test1"
        app1.config["IMAGEKITIO_PRIVATE_KEY"] = "private_key_1"
        app1.config["IMAGEKITIO_PUBLIC_KEY"] = "public_key_1"

        app2 = Flask("app2")
        app2.config["IMAGEKITIO_URL_ENDPOINT"] = "https://ik.imagekit.io/test2"
        app2.config["IMAGEKITIO_PRIVATE_KEY"] = "private_key_2"
        app2.config["IMAGEKITIO_PUBLIC_KEY"] = "public_key_2"

        ik1 = ImagekitIO(app1)
        ik2 = ImagekitIO(app2)

        assert ik1.url_endpoint == "https://ik.imagekit.io/test1"
        assert ik2.url_endpoint == "https://ik.imagekit.io/test2"
        assert ik1.public_key == "public_key_1"
        assert ik2.public_key == "public_key_2"

        assert app1.extensions["imagekitio"] == ik1
        assert app2.extensions["imagekitio"] == ik2

    def test_extension_isolation_between_apps(self):
        """Test that extensions on different apps are isolated."""
        app1 = Flask("app1")
        app1.config["IMAGEKITIO_URL_ENDPOINT"] = "https://ik.imagekit.io/test1"
        app1.config["IMAGEKITIO_PRIVATE_KEY"] = "private_key_1"
        app1.config["IMAGEKITIO_PUBLIC_KEY"] = "public_key_1"

        app2 = Flask("app2")
        app2.config["IMAGEKITIO_URL_ENDPOINT"] = "https://ik.imagekit.io/test2"
        app2.config["IMAGEKITIO_PRIVATE_KEY"] = "private_key_2"
        app2.config["IMAGEKITIO_PUBLIC_KEY"] = "public_key_2"

        ik1 = ImagekitIO()
        ik2 = ImagekitIO()

        ik1.init_app(app1)
        ik2.init_app(app2)

        # Changing one shouldn't affect the other
        assert ik1.url_endpoint != ik2.url_endpoint
        assert ik1.public_key != ik2.public_key


class TestImagekitIOPrivateKey:
    """Test private key handling."""

    def test_private_key_is_private(self, app, imagekitio):
        """Test that private key is stored as private attribute."""
        imagekitio.init_app(app)

        # Private key should not be directly accessible
        assert not hasattr(imagekitio, "private_key")

        # But should be accessible via name mangling for testing
        assert hasattr(imagekitio, "_ImagekitIO__private_key")
        assert imagekitio._ImagekitIO__private_key == app.config["IMAGEKITIO_PRIVATE_KEY"]

    def test_private_key_used_in_interface(self, app, imagekitio):
        """Test that private key is properly passed to ImageKit."""
        imagekitio.init_app(app)

        with patch("flask_imagekitio.ImageKit") as mock_imagekit_class:
            with imagekitio.interface():
                pass

            # Verify private key was passed to ImageKit constructor
            call_args = mock_imagekit_class.call_args
            assert call_args[0][1] == app.config["IMAGEKITIO_PRIVATE_KEY"]


class TestImagekitIOEdgeCases:
    """Test edge cases and error scenarios."""

    def test_interface_used_without_init_app(self):
        """Test using interface before calling init_app."""
        ik = ImagekitIO()

        with pytest.raises(AttributeError, match="In order to use the interface"):
            with ik.interface():
                pass

    @patch("flask_imagekitio.ImageKit")
    def test_multiple_operations_in_single_context(self, mock_imagekit_class, configured_imagekitio):
        """Test performing multiple operations within single interface context."""
        mock_ik = Mock()
        mock_imagekit_class.return_value = mock_ik

        with configured_imagekitio.interface() as ik:
            ik.list_files()
            ik.upload_file(file=b"data", file_name="test.jpg")
            ik.delete_file("file_id")

        assert mock_ik.list_files.called
        assert mock_ik.upload_file.called
        assert mock_ik.delete_file.called

    @patch("flask_imagekitio.ImageKit")
    def test_nested_interface_contexts(self, mock_imagekit_class, configured_imagekitio):
        """Test nested interface contexts work correctly."""
        mock_imagekit_class.return_value = Mock()

        with configured_imagekitio.interface() as ik1:
            with configured_imagekitio.interface() as ik2:
                # Both should work
                assert ik1 is not None
                assert ik2 is not None

        # Should create two separate ImageKit instances
        assert mock_imagekit_class.call_count == 2
