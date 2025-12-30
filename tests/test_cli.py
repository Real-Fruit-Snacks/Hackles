"""Tests for CLI argument parsing"""
import pytest
from unittest.mock import patch


class TestCliParser:
    """Test CLI argument parsing."""

    def test_parser_creation(self):
        """Test parser is created successfully."""
        from hackles.cli.parser import create_parser

        parser = create_parser()
        assert parser is not None

    def test_required_password_argument(self):
        """Test password is required."""
        from hackles.cli.parser import create_parser

        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_default_values(self):
        """Test default argument values."""
        from hackles.cli.parser import create_parser

        parser = create_parser()
        args = parser.parse_args(['-p', 'testpass'])

        assert args.bolt == 'bolt://127.0.0.1:7687'
        assert args.username == 'neo4j'
        assert args.password == 'testpass'
        assert args.quiet is False
        assert args.debug is False
        assert args.all is False

    def test_category_flags(self):
        """Test category flags are parsed correctly."""
        from hackles.cli.parser import create_parser

        parser = create_parser()
        args = parser.parse_args(['-p', 'pass', '--acl', '--adcs', '--privesc'])

        assert args.acl is True
        assert args.adcs is True
        assert args.privesc is True
        assert args.hygiene is False

    def test_output_format_flags(self):
        """Test output format flags."""
        from hackles.cli.parser import create_parser

        parser = create_parser()

        # JSON output
        args = parser.parse_args(['-p', 'pass', '--json'])
        assert args.json is True

        # CSV output
        args = parser.parse_args(['-p', 'pass', '--csv'])
        assert args.csv is True

        # HTML output
        args = parser.parse_args(['-p', 'pass', '--html', 'report.html'])
        assert args.html == 'report.html'

    def test_quick_filter_flags(self):
        """Test quick filter flags."""
        from hackles.cli.parser import create_parser

        parser = create_parser()
        args = parser.parse_args(['-p', 'pass', '--kerberoastable'])
        assert args.kerberoastable is True

        args = parser.parse_args(['-p', 'pass', '--asrep'])
        assert args.asrep is True

        args = parser.parse_args(['-p', 'pass', '--unconstrained'])
        assert args.unconstrained is True

    def test_path_finding_arguments(self):
        """Test path finding arguments."""
        from hackles.cli.parser import create_parser

        parser = create_parser()

        # Two-node path
        args = parser.parse_args(['-p', 'pass', '--path', 'USER@DOM', 'DC01@DOM'])
        assert args.path == ['USER@DOM', 'DC01@DOM']

        # Path to DA
        args = parser.parse_args(['-p', 'pass', '--path-to-da', 'USER@DOM'])
        assert args.path_to_da == 'USER@DOM'

    def test_owned_management_arguments(self):
        """Test owned management arguments."""
        from hackles.cli.parser import create_parser

        parser = create_parser()

        # Mark owned (can be repeated)
        args = parser.parse_args(['-p', 'pass', '-o', 'USER1@DOM', '-o', 'USER2@DOM'])
        assert args.own == ['USER1@DOM', 'USER2@DOM']

        # Clear owned
        args = parser.parse_args(['-p', 'pass', '--clear-owned'])
        assert args.clear_owned is True

    def test_severity_filter_argument(self):
        """Test severity filter argument."""
        from hackles.cli.parser import create_parser

        parser = create_parser()
        args = parser.parse_args(['-p', 'pass', '--severity', 'CRITICAL,HIGH'])
        assert args.severity == 'CRITICAL,HIGH'

    def test_stats_flag(self):
        """Test --stats flag."""
        from hackles.cli.parser import create_parser

        parser = create_parser()
        args = parser.parse_args(['-p', 'pass', '--stats'])
        assert args.stats is True


class TestCategoryMapping:
    """Test CLI category flag to registry category mapping."""

    def test_category_flags_mapping(self):
        """Test CATEGORY_FLAGS mapping is complete."""
        from hackles.cli.main import CATEGORY_FLAGS

        expected_flags = [
            'acl', 'adcs', 'attack_paths', 'azure', 'basic',
            'groups', 'delegation', 'exchange', 'lateral',
            'misc', 'owned_queries', 'privesc', 'hygiene'
        ]

        for flag in expected_flags:
            assert flag in CATEGORY_FLAGS, f"Missing category flag: {flag}"
