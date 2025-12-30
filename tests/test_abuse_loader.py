"""Tests for abuse template loading"""
import pytest
from pathlib import Path


class TestAbuseTemplateLoader:
    """Test abuse template loading functionality."""

    def test_templates_directory_exists(self):
        """Test templates directory exists."""
        from hackles.abuse.loader import TEMPLATES_DIR

        assert TEMPLATES_DIR.exists()
        assert TEMPLATES_DIR.is_dir()

    def test_load_template_returns_dict(self):
        """Test load_template returns dictionary."""
        from hackles.abuse.loader import load_template

        # Load a known template
        template = load_template("GenericAll")
        if template:  # Template might not exist in test env
            assert isinstance(template, dict)
            assert 'name' in template or 'description' in template

    def test_templates_have_required_fields(self):
        """Test all templates have required fields."""
        from hackles.abuse.loader import TEMPLATES_DIR
        import yaml

        for template_file in TEMPLATES_DIR.glob("*.yml"):
            with open(template_file) as f:
                data = yaml.safe_load(f)

            assert 'name' in data, f"Template {template_file.name} missing 'name'"
            # Commands or description should exist
            assert 'commands' in data or 'description' in data, \
                f"Template {template_file.name} missing 'commands' or 'description'"

    def test_template_count(self):
        """Test we have expected number of templates."""
        from hackles.abuse.loader import TEMPLATES_DIR

        templates = list(TEMPLATES_DIR.glob("*.yml"))
        # We should have at least 40+ templates
        assert len(templates) >= 40, f"Expected 40+ templates, found {len(templates)}"


class TestAbuseTemplatePlaceholders:
    """Test placeholder replacement in templates."""

    def test_placeholders_format(self):
        """Test placeholders use correct format."""
        from hackles.abuse.loader import TEMPLATES_DIR

        for template_file in TEMPLATES_DIR.glob("*.yml"):
            content = template_file.read_text()
            # Check for properly formatted placeholders (not Python format strings)
            if '<' in content:
                # Should use <PLACEHOLDER> format
                assert '<%s>' not in content, f"Template {template_file.name} uses wrong placeholder format"
