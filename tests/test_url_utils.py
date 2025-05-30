# tests/test_url_utils.py
from page_loader.url_utils import (
    filename_from_url,
    filename_from_full_url,
    full_url,
    base_url,
    dirname_for_web_assets,
    scheme,
    domain,
    full_domain,
    extension,
    file_name,
    is_absolute_path
)


def test_filename_from_url():
    assert (filename_from_url('/assets/img/omelette.png')
            == 'assets-img-omelette.png')

    assert (
        filename_from_url('https://lorem.dot.net/assets/omelette.html')
        == 'lorem-dot-net-assets-omelette.html'
    )

    assert (
        filename_from_url('http://lorem.dot.net/assets/omelette')
        == 'lorem-dot-net-assets-omelette.html'
    )

    assert (
        filename_from_url('http://lorem.dot.net/assets/omelette/')
        == 'lorem-dot-net-assets-omelette.html'
    )

    assert (filename_from_url('https://ru.hexlet.io/packs/js/runtime.js')
            == 'ru-hexlet-io-packs-js-runtime.js')


def test_filename_from_full_url():
    assert (filename_from_full_url('https://ru.hexlet.io/packs/js/runtime.js')
            == 'ru-hexlet-io-packs-js-runtime.js')


def test_dirname_for_web_resources():
    assert (dirname_for_web_assets('lorem-github-io-web_page.html')
            == 'lorem-github-io-web_page_files')
    assert (dirname_for_web_assets('lorem-github-io-web_page.html', 'resources')
            == 'lorem-github-io-web_page_resources')


def test_full_url():
    assert full_url('https://lorem.dot.net') == 'https://lorem.dot.net'

    assert (full_url('https://lorem.dot.net/site/index.html')
            == 'https://lorem.dot.net/site/index.html')

    assert (full_url('https://lorem.dot.net/site/logo.png')
            == 'https://lorem.dot.net/site/logo.png')

    assert (full_url('https://lorem.dot.net/site/')
            == 'https://lorem.dot.net/site/index.html')

    assert (full_url('https://lorem.dot.net/site')
            == 'https://lorem.dot.net/site/index.html')

    assert (full_url('https://lorem.dot.net/site', 'main.html')
            == 'https://lorem.dot.net/site/main.html')


def test_base_url():
    assert (base_url('https://lorem.dot.net/site/index.html')
            == 'https://lorem.dot.net/site/')

    assert (base_url('https://lorem.dot.net/site/')
            == 'https://lorem.dot.net/site/')

    assert (base_url('https://lorem.dot.net/site')
            == 'https://lorem.dot.net/site/')


def test_scheme():
    assert scheme('lorem/assets/professions/python.png') == ''
    assert scheme('https://lorem.dot.net/assets/python.png') == 'https'


def test_domain():
    assert domain('lorem/assets/professions/python.png') == ''
    assert (
        domain('https://lorem.dot.net/professions/assets/python.png')
        == 'lorem.dot.net')


def test_full_domain():
    assert (full_domain('https://lorem.dot.net/professions/assets/python.png')
            == 'https://lorem.dot.net')
    assert (full_domain('https://lorem.dot.net')
            == 'https://lorem.dot.net')


def test_file_name():
    assert (file_name('https://lorem.dot.net/professions/assets/python.png')
            == 'python.png')
    assert file_name('https://lorem.dot.net') == ''
    assert file_name('https://lorem.dot.net/professions/') == ''


def test_extension():
    assert extension('https://lorem.dot.net/lib/bio.dhtml') == 'dhtml'
    assert extension('https://lorem.dot.net/some_web_page/') == ''


def test_is_absolute_path():
    assert is_absolute_path('/assets/professions/python.png')
    assert not is_absolute_path('assets/professions/python.png')
