import pytest

from mm_std import parse_lines, str_contains_any, str_ends_with_any, str_starts_with_any


class TestStrStartsWithAny:
    @pytest.mark.parametrize(
        "text,prefixes,expected",
        [
            ("hello world", ["hello"], True),
            ("test string", ["test", "other"], True),
            ("hello world", ["world"], False),
            ("https://example.com", ["http://", "https://", "ftp://"], True),
            ("ftp://files.example.com", ["http://", "https://", "ftp://"], True),
            ("mailto:test@example.com", ["http://", "https://", "ftp://"], False),
        ],
    )
    def test_basic_matching(self, text, prefixes, expected):
        assert str_starts_with_any(text, prefixes) == expected

    @pytest.mark.parametrize(
        "text,prefixes",
        [
            ("hello", []),
            ("", ["prefix"]),
        ],
    )
    def test_empty_inputs_return_false(self, text, prefixes):
        assert not str_starts_with_any(text, prefixes)

    def test_empty_string_matches_empty_prefix(self):
        assert str_starts_with_any("", [""])

    @pytest.mark.parametrize(
        "text,case_match,case_no_match",
        [
            ("Hello", "Hello", "hello"),
            ("FILE.TXT", "FILE", "file"),
        ],
    )
    def test_case_sensitivity(self, text, case_match, case_no_match):
        assert str_starts_with_any(text, [case_match])
        assert not str_starts_with_any(text, [case_no_match])

    @pytest.mark.parametrize(
        "iterable_type",
        [
            lambda items: items,  # list
            lambda items: tuple(items),  # tuple
            lambda items: set(items),  # set
            lambda items: (i for i in items),  # generator
        ],
    )
    def test_accepts_different_iterables(self, iterable_type):
        text = "hello world"
        prefixes = iterable_type(["hello", "hi"])
        assert str_starts_with_any(text, prefixes)


class TestStrEndsWithAny:
    @pytest.mark.parametrize(
        "filename,extensions,expected",
        [
            ("document.pdf", [".pdf"], True),
            ("image.png", [".jpg", ".png", ".gif"], True),
            ("script.py", [".js", ".ts", ".go"], False),
            ("archive.tar.gz", [".tar.gz", ".zip"], True),
        ],
    )
    def test_file_extensions(self, filename, extensions, expected):
        assert str_ends_with_any(filename, extensions) == expected

    @pytest.mark.parametrize(
        "text,suffixes",
        [
            ("hello.txt", []),
            ("", ["suffix"]),
        ],
    )
    def test_empty_inputs_return_false(self, text, suffixes):
        assert not str_ends_with_any(text, suffixes)

    def test_empty_string_matches_empty_suffix(self):
        assert str_ends_with_any("", [""])

    @pytest.mark.parametrize(
        "filename,case_match,case_no_match",
        [
            ("file.TXT", ".TXT", ".txt"),
            ("IMAGE.PNG", ".PNG", ".png"),
        ],
    )
    def test_case_sensitivity(self, filename, case_match, case_no_match):
        assert str_ends_with_any(filename, [case_match])
        assert not str_ends_with_any(filename, [case_no_match])

    def test_accepts_different_iterables(self):
        filename = "document.pdf"
        assert str_ends_with_any(filename, [".pdf"])  # list
        assert str_ends_with_any(filename, (".pdf", ".doc"))  # tuple
        assert str_ends_with_any(filename, {".pdf", ".doc"})  # set


class TestStrContainsAny:
    @pytest.mark.parametrize(
        "text,substrings,expected",
        [
            ("hello world", ["world"], True),
            ("error: file not found", ["error", "warning", "critical"], True),
            ("[warning] Low disk space", ["error", "warning", "critical"], True),
            ("Everything is fine", ["error", "warning", "critical"], False),
            ("programming language", ["gram", "lang"], True),
        ],
    )
    def test_log_level_detection(self, text, substrings, expected):
        assert str_contains_any(text, substrings) == expected

    @pytest.mark.parametrize(
        "text,substrings",
        [
            ("hello world", []),
            ("", ["substring"]),
        ],
    )
    def test_empty_inputs_return_false(self, text, substrings):
        assert not str_contains_any(text, substrings)

    def test_empty_string_contains_empty_substring(self):
        assert str_contains_any("", [""])

    @pytest.mark.parametrize(
        "text,case_match,case_no_match",
        [
            ("Hello World", "World", "world"),
            ("ERROR: Critical failure", "ERROR", "error"),
        ],
    )
    def test_case_sensitivity(self, text, case_match, case_no_match):
        assert str_contains_any(text, [case_match])
        assert not str_contains_any(text, [case_no_match])

    @pytest.mark.parametrize(
        "text,overlapping_substrings",
        [
            ("programming", ["gram", "gramming"]),
            ("development", ["dev", "develop"]),
        ],
    )
    def test_overlapping_substrings(self, text, overlapping_substrings):
        assert str_contains_any(text, overlapping_substrings)

    def test_accepts_different_iterables(self):
        text = "hello world"
        assert str_contains_any(text, ["world"])  # list
        assert str_contains_any(text, ("world", "earth"))  # tuple
        assert str_contains_any(text, {"world", "earth"})  # set


class TestParseLines:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("line1\nline2\nline3", ["line1", "line2", "line3"]),
            ("single line", ["single line"]),
            ("", []),
            ("   \n\t\n  ", []),
        ],
    )
    def test_basic_parsing(self, text, expected):
        assert parse_lines(text) == expected

    def test_whitespace_handling(self):
        text = "line1\n\n  \nline2\n   line3   \n\nline4"
        expected = ["line1", "line2", "line3", "line4"]
        assert parse_lines(text) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("HELLO\nWorld\nTEST", ["hello", "world", "test"]),
            ("Mixed\nCASE\ntext", ["mixed", "case", "text"]),
        ],
    )
    def test_lowercase_conversion(self, text, expected):
        assert parse_lines(text, lowercase=True) == expected

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("line1 # comment\nline2\nline3 # another", ["line1", "line2", "line3"]),
            ("line1#no space\n#comment only\nline2 # normal", ["line1", "line2"]),
            ("# comment1\n# comment2", []),
        ],
    )
    def test_comment_removal(self, text, expected):
        assert parse_lines(text, remove_comments=True) == expected

    def test_deduplication_preserves_order(self):
        text = "line1\nline2\nline1\nline3\nline2\nline4"
        expected = ["line1", "line2", "line3", "line4"]
        assert parse_lines(text, deduplicate=True) == expected

    def test_combined_options(self):
        text = "HELLO # comment\nworld\nHELLO # different\nTEST\nworld"
        expected = ["hello", "world", "test"]
        result = parse_lines(text, lowercase=True, remove_comments=True, deduplicate=True)
        assert result == expected
