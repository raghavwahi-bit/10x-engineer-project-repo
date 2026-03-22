"""Tests for utility functions."""

from datetime import datetime, timedelta

from app.models import Prompt
from app.utils import (
    sort_prompts_by_date,
    filter_prompts_by_collection,
    search_prompts,
    validate_prompt_content,
    extract_variables,
)


def _make_prompt(title="Test", content="Content", **kwargs):
    """Helper to create a Prompt with specified fields."""
    return Prompt(title=title, content=content, **kwargs)


class TestSortPromptsByDate:
    """Tests for sort_prompts_by_date function."""

    def test_sort_descending_default(self):
        now = datetime.utcnow()
        p1 = _make_prompt(title="Old")
        p1.created_at = now - timedelta(hours=2)
        p2 = _make_prompt(title="New")
        p2.created_at = now
        result = sort_prompts_by_date([p1, p2])
        assert result[0].title == "New"
        assert result[1].title == "Old"

    def test_sort_ascending(self):
        now = datetime.utcnow()
        p1 = _make_prompt(title="Old")
        p1.created_at = now - timedelta(hours=2)
        p2 = _make_prompt(title="New")
        p2.created_at = now
        result = sort_prompts_by_date([p1, p2], descending=False)
        assert result[0].title == "Old"
        assert result[1].title == "New"

    def test_sort_empty_list(self):
        result = sort_prompts_by_date([])
        assert result == []

    def test_sort_single_item(self):
        p = _make_prompt(title="Only")
        result = sort_prompts_by_date([p])
        assert len(result) == 1
        assert result[0].title == "Only"


class TestFilterPromptsByCollection:
    """Tests for filter_prompts_by_collection function."""

    def test_filter_matching_collection(self):
        p1 = _make_prompt(title="Match", collection_id="col-1")
        p2 = _make_prompt(title="NoMatch", collection_id="col-2")
        result = filter_prompts_by_collection([p1, p2], "col-1")
        assert len(result) == 1
        assert result[0].title == "Match"

    def test_filter_no_match(self):
        p1 = _make_prompt(collection_id="col-1")
        result = filter_prompts_by_collection([p1], "col-999")
        assert result == []

    def test_filter_empty_list(self):
        result = filter_prompts_by_collection([], "col-1")
        assert result == []

    def test_filter_none_collection_id_excluded(self):
        p1 = _make_prompt(collection_id=None)
        p2 = _make_prompt(collection_id="col-1")
        result = filter_prompts_by_collection([p1, p2], "col-1")
        assert len(result) == 1


class TestSearchPrompts:
    """Tests for search_prompts function."""

    def test_search_title_match(self):
        p = _make_prompt(title="Hello World")
        result = search_prompts([p], "hello")
        assert len(result) == 1

    def test_search_description_match(self):
        p = _make_prompt(description="Find this keyword")
        result = search_prompts([p], "keyword")
        assert len(result) == 1

    def test_search_case_insensitive(self):
        p = _make_prompt(title="UPPERCASE Title")
        result = search_prompts([p], "uppercase")
        assert len(result) == 1

    def test_search_no_match(self):
        p = _make_prompt(title="Hello", description="World")
        result = search_prompts([p], "xyz")
        assert result == []

    def test_search_none_description(self):
        p = _make_prompt(title="Hello", description=None)
        result = search_prompts([p], "Hello")
        assert len(result) == 1

    def test_search_partial_match(self):
        p = _make_prompt(title="Programming tutorial")
        result = search_prompts([p], "gram")
        assert len(result) == 1

    def test_search_empty_list(self):
        result = search_prompts([], "query")
        assert result == []


class TestValidatePromptContent:
    """Tests for validate_prompt_content function."""

    def test_valid_content(self):
        assert validate_prompt_content("This is valid content") is True

    def test_empty_string(self):
        assert validate_prompt_content("") is False

    def test_whitespace_only(self):
        assert validate_prompt_content("         ") is False

    def test_exactly_10_chars(self):
        assert validate_prompt_content("1234567890") is True

    def test_9_chars(self):
        assert validate_prompt_content("123456789") is False

    def test_content_with_whitespace_stripped_valid(self):
        assert validate_prompt_content("  1234567890  ") is True

    def test_content_with_whitespace_stripped_invalid(self):
        assert validate_prompt_content("  123456   ") is False


class TestExtractVariables:
    """Tests for extract_variables function."""

    def test_single_variable(self):
        result = extract_variables("Hello {{name}}!")
        assert result == ["name"]

    def test_multiple_variables(self):
        result = extract_variables("{{greeting}} {{name}}, welcome to {{place}}")
        assert result == ["greeting", "name", "place"]

    def test_no_variables(self):
        result = extract_variables("No variables here")
        assert result == []

    def test_duplicate_variables(self):
        result = extract_variables("{{name}} and {{name}}")
        assert result == ["name", "name"]

    def test_variable_with_underscores(self):
        result = extract_variables("{{first_name}} {{last_name}}")
        assert result == ["first_name", "last_name"]

    def test_empty_string(self):
        result = extract_variables("")
        assert result == []

    def test_nested_braces_not_matching(self):
        result = extract_variables("{{{name}}}")
        assert "name" in result

    def test_single_braces_not_matching(self):
        result = extract_variables("{name}")
        assert result == []
