from unittest.mock import patch

APP_PATH = "../tofuref/main.py"

SEARCH_GITHUB = ["s", "g", "i", "t", "h", "u", "b"]


def test_welcome(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, terminal_size=(200, 60))


def test_welcome_fullscreen(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH)


@patch("tofuref.__version__", "1.0.0")
def test_welcome_update_available(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH)


def test_toggle_fullscreen(snap_compare, clear_mock_cache):
    # Result: fullscreen mode off, even though it's a small window
    assert snap_compare(APP_PATH, press=["f"])


def test_content(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "pagedown"])


def test_content_toc_on(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "t"])


def test_content_toc_off(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "t", "t"])


def test_content_toc_submit(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "t", "down", "down", "down", "down", "down", "enter"])


def test_use_none_selected(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=["u"])


def test_search_github(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=SEARCH_GITHUB)


def test_search_github_cancel(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "escape"])


def test_open_github(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter"])


def test_open_github_membership(snap_compare):
    assert snap_compare(
        APP_PATH,
        press=[*SEARCH_GITHUB, "enter", "enter", "s", "m", "e", "m", "b", "e", "r", "enter", "enter"],
    )


def test_back_to_providers(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=["enter", "p"])


def test_provider_overview(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c"])


def test_version_picker(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "v"])


def test_version_picker_submit(snap_compare):
    assert snap_compare(
        APP_PATH,
        press=[*SEARCH_GITHUB, "enter", "enter", "v", "down", "enter"],
    )


def test_use(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "u"])


def test_copy_selection_github_overview(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c", "y"])


def test_copy_selection_github_overview_copy_first(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c", "y", "enter"])


def test_vim_providers(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=["j"])


def test_vim_resources(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=["enter", "j"])


def test_vim_content(snap_compare):
    assert snap_compare(APP_PATH, press=["c", "j"])


# For some reason the theme persists? Commented out for now
# def test_config_theme(snap_compare):
#     os.environ["TOFUREF_THEME_UI"] = "monokai"
#     os.environ["TOFUREF_THEME_CODEBLOCKS"] = "monokai"
#     os.environ["TOFUREF_THEME_BORDERS_STYLE"] = "solid"
#     assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "c", "wait:500", "pagedown"])
#     os.environ.pop("TOFUREF_THEME_UI")
#     os.environ.pop("TOFUREF_THEME_CODEBLOCKS")
#     os.environ.pop("TOFUREF_THEME_BORDERS_STYLE")


def test_recent_provider(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "p"])


def test_recent_resource(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "enter", "r"])


def test_bookmark_provider(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "b"])


def test_bookmark_resource(snap_compare):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "b"])


def test_bookmark_cached_provider(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "p", "b"])


def test_bookmark_cached_resource(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "enter", "r", "b"])


def test_clear_from_cache(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=[*SEARCH_GITHUB, "enter", "enter", "p", "ctrl+d"])


def test_stats(snap_compare, clear_mock_cache):
    assert snap_compare(APP_PATH, press=["ctrl+s"])
