import os
import pytest
import stat

from page_loader import download
from page_loader.exceptions.io_exceptions import SaveError, DirectoryError
from page_loader.exceptions.network_exceptions import HttpError, RequestError

from fixtures.fixtures import (
    URL,
    ASSETS_DIR,
    CONTENT_FILE,
    ASSETS,
    HTTP_ERROR_CODES,
    compare_prettified_htmls,
    retrieved_content,
    expected_content,
    cleanup_downloaded_files,
    setup_mocking,
    setup_mocking_http_fail_response,
    setup_mocking_request_exception,
    temp_directory
)


# Test the download of HTML content
@pytest.mark.parametrize(
    'filename', ['retrieved.html'])
def test_download_html(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        result_path = download(URL, path=temp_dir)

        assert os.path.isfile(result_path), "Downloaded HTML file should exist"

        html_path = os.path.join(
            temp_dir, CONTENT_FILE
        )
        assert result_path == html_path, \
            "Downloaded HTML file path should match the expected path"
        with open(result_path, 'r') as f:
            assert compare_prettified_htmls(f.read(), expected_content), \
                "Downloaded HTML content should match the expected content"


# Test the download of assets and ensure proper link transformation
@pytest.mark.parametrize('filename', ['retrieved.html'])
def test_download_assets(
        expected_content, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        download(URL, path=temp_dir)
        assets_dir_path = os.path.join(temp_dir, ASSETS_DIR)
        assert os.path.exists(assets_dir_path), \
            "Assets directory should exist"
        assert os.path.isdir(assets_dir_path), \
            "Assets path should be a directory"

        html_path = os.path.join(temp_dir, CONTENT_FILE)
        with open(html_path, 'r') as file:
            html_content = file.read()

        for asset_data in ASSETS:
            path = asset_data['path']
            link = os.path.join(ASSETS_DIR, path)
            assert link in html_content, \
                f"Link {link} should be present in HTML content"

            asset_path = os.path.join(assets_dir_path, path)
            assert os.path.isfile(asset_path), \
                f"Asset file {asset_path} should exist"

            content = asset_data['content']

            if asset_data['url'].endswith('html'):
                assert compare_prettified_htmls(
                    open(asset_path).read(), content), \
                    f"HTML content of {asset_path} should match"
            else:
                assert open(asset_path).read() == content, \
                    f"Content of {asset_path} should match"

        # Check that images from external links are not saved
        external_asset_files = [
            file for file in os.listdir(assets_dir_path)
            if "external-" in file
        ]
        assert not external_asset_files, \
            "External image files should not be saved"


@pytest.mark.parametrize('filename', ['retrieved_without_assets.html'])
def test_download_html_without_assets_to_download(
        filename, retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        download(URL, path=temp_dir)
        assets_dir_path = os.path.join(temp_dir, ASSETS_DIR)
        assert not os.path.exists(assets_dir_path), \
            f"The assets directory '{ASSETS_DIR}' should not exist"


@pytest.mark.parametrize(
    'filename', ['retrieved.html', 'retrieved_without_assets.html'])
def test_download_return_value_with_none_path(
        retrieved_content, setup_mocking, cleanup_downloaded_files):
    with setup_mocking:
        result_path = download(URL)
        assert os.path.isfile(result_path), \
            f"Downloaded file {result_path} should exist"
        assert result_path == 'ru-hexlet-io-courses.html', \
            f'Downloaded file path should be {CONTENT_FILE}'


# Test the processing of an attempt to save content with access rights issues
# TODO: Perhaps the test should be generalized
# TODO: Or add other scenarios - for example, when there's no enough disk space
@pytest.mark.parametrize(
    'filename', ['retrieved.html', 'retrieved_without_assets.html'])
def test_save_error_permission_issue(
        retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        html_path = os.path.join(temp_dir, CONTENT_FILE)
        with open(html_path, 'w'):
            pass
        os.chmod(html_path, stat.S_IREAD)

        with pytest.raises(SaveError) as e:
            result_path = download(URL, path=temp_dir)

            assert result_path is None, \
                ("If there is a save error due to permission issues, "
                 "download should fail and result_path should be None")

        error_message_pattern = (f"Failed to save page content to {html_path}. "
                                 f"Error: [Errno 13] Permission denied")

        assert error_message_pattern in str(e.value)

        # TODO: implement logic to pass it
        # import pdb; pdb.set_trace()
        unexpected_files = [file_name for file_name in os.listdir(temp_dir)
                            if file_name != CONTENT_FILE]
        assert not any(unexpected_files), \
            (f'No files (except for {CONTENT_FILE}) should remain in '
             f'the destination directory if the download fails.')


# Test the processing of a missing destination directory during download
@pytest.mark.parametrize(
    'filename', ['retrieved.html', 'retrieved_without_assets.html'])
def test_missing_destination_directory_issue(
        retrieved_content, setup_mocking, temp_directory):
    with setup_mocking, temp_directory as temp_dir:
        os.rmdir(temp_dir)
        with pytest.raises(DirectoryError) as e:
            result_path = download(URL, path=temp_dir)

            assert result_path is None, \
                ('If the destination directory is missing, '
                 'download should fail and result_path should be None')

    error_message = f"Directory '{temp_dir}' does not exist."
    assert str(e.value) == error_message


# Test the processing of various HTTP error responses
@pytest.mark.parametrize('status_code', HTTP_ERROR_CODES)
def test_download_html_with_http_fail_response(
        setup_mocking_http_fail_response, temp_directory, status_code):

    with setup_mocking_http_fail_response, temp_directory as temp_dir:
        with pytest.raises(HttpError) as e:
            result_path = download(URL, path=temp_dir)

            assert result_path is None, (
                "If there is an HTTP error response, "
                "download should fail and result_path should be None"
            )

        assert not any(os.listdir(temp_dir)), \
            ('No files should be created in the destination directory '
             'if the download fails')

        error_message = (f'Failed to retrieve content. '
                         f'Server returned status code {status_code}')
        assert str(e.value) == error_message


# Test the processing of RequestException during download
def test_download_html_with_request_error(
        setup_mocking_request_exception, temp_directory):

    with setup_mocking_request_exception, temp_directory as temp_dir:
        with pytest.raises(RequestError) as e:
            result_path = download(URL, path=temp_dir)

            assert result_path is None, (
                "If there is an HTTP error response, "
                "download should fail and result_path should be None"
            )

        assert not any(os.listdir(temp_dir)), \
            ('No files should be created in the destination directory '
             'if the download fails')

        error_message = \
            ('Failed to retrieve content. '
             'Error: Some simulated RequestException')
        assert str(e.value) == error_message
