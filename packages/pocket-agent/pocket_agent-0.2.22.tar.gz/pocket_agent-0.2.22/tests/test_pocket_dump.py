import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import argparse

from pocket_agent.pocket_dump.cli import (
    find_pocket_agent_files,
    find_documentation_files,
    read_file_safely,
    count_lines_and_chars,
    generate_markdown_documentation,
    get_version,
    main
)


class TestFileDiscovery:
    """Test file discovery functions"""
    
    def test_find_documentation_files_with_docs(self, tmp_path):
        """Test finding documentation files when docs directory exists"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        # Create docs directory with files
        docs_path = base_path / "docs"
        docs_path.mkdir()
        
        (docs_path / "00_index.md").write_text("# Index")
        (docs_path / "01_getting-started.md").write_text("# Getting Started")
        (docs_path / "02_core-concepts.md").write_text("# Core Concepts")
        
        doc_files = find_documentation_files(base_path)
        
        assert len(doc_files) == 3
        # Files should be sorted
        assert doc_files[0].name == "00_index.md"
        assert doc_files[1].name == "01_getting-started.md"
        assert doc_files[2].name == "02_core-concepts.md"
    
    def test_find_documentation_files_no_docs(self, tmp_path):
        """Test finding documentation files when docs directory doesn't exist"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        doc_files = find_documentation_files(base_path)
        
        assert len(doc_files) == 0
    
    def test_find_documentation_files_empty_docs(self, tmp_path):
        """Test finding documentation files when docs directory is empty"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        docs_path = base_path / "docs"
        docs_path.mkdir()
        
        doc_files = find_documentation_files(base_path)
        
        assert len(doc_files) == 0


class TestFileOperations:
    """Test file reading and processing functions"""
    
    def test_read_file_safely_success(self, tmp_path):
        """Test successfully reading a file"""
        test_file = tmp_path / "test.py"
        content = "# Test Python file\nprint('hello world')"
        test_file.write_text(content)
        
        result = read_file_safely(test_file)
        
        assert result == content
    
    def test_read_file_safely_file_not_found(self, tmp_path):
        """Test reading a non-existent file"""
        non_existent = tmp_path / "does_not_exist.py"
        
        result = read_file_safely(non_existent)
        
        assert "Error reading file" in result
    
    def test_read_file_safely_permission_error(self, tmp_path):
        """Test reading a file with permission issues"""
        test_file = tmp_path / "restricted.py"
        test_file.write_text("content")
        
        # Mock a permission error
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            result = read_file_safely(test_file)
        
        assert "Error reading file" in result
        assert "Access denied" in result
    
    def test_count_lines_and_chars(self):
        """Test line and character counting"""
        content = "Line 1\nLine 2\nLine 3"
        
        lines, chars = count_lines_and_chars(content)
        
        assert lines == 3
        assert chars == len(content)
    
    def test_count_lines_and_chars_empty(self):
        """Test counting empty content"""
        lines, chars = count_lines_and_chars("")
        
        assert lines == 1  # Empty string has 1 line
        assert chars == 0
    
    def test_count_lines_and_chars_single_line(self):
        """Test counting single line content"""
        content = "Single line without newline"
        
        lines, chars = count_lines_and_chars(content)
        
        assert lines == 1
        assert chars == len(content)


class TestMarkdownGeneration:
    """Test markdown document generation"""
    
    def test_generate_markdown_docs_and_source(self, tmp_path):
        """Test generating markdown with both docs and source"""
        # Create test files
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        source_file = base_path / "agent.py"
        source_file.write_text("# Agent code\nclass PocketAgent:\n    pass")
        
        docs_path = base_path / "docs"
        docs_path.mkdir()
        doc_file = docs_path / "01_guide.md"
        doc_file.write_text("# Guide\nThis is a guide.")
        
        source_files = [source_file]
        doc_files = [doc_file]
        
        result = generate_markdown_documentation(
            source_files, doc_files, base_path, 
            include_docs=True, include_source=True
        )
        
        # Check table of contents
        assert "📖 Documentation:" in result
        assert "🔧 Source Code:" in result
    
    def test_generate_markdown_source_only(self, tmp_path):
        """Test generating markdown with source only"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        source_file = base_path / "client.py"
        source_file.write_text("# Client code\nclass Client:\n    pass")
        
        source_files = [source_file]
        doc_files = []
        
        result = generate_markdown_documentation(
            source_files, doc_files, base_path,
            include_docs=False, include_source=True
        )
        assert "**📖 Documentation Files:** 0 files (excluded)" in result
        assert "📖 Documentation:" not in result
        assert "🔧 Source Code:" in result
    
    def test_generate_markdown_docs_only(self, tmp_path):
        """Test generating markdown with docs only"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        docs_path = base_path / "docs"
        docs_path.mkdir()
        doc_file = docs_path / "00_index.md"
        doc_file.write_text("# Documentation Index\nWelcome to docs.")
        
        source_files = []
        doc_files = [doc_file]
        
        result = generate_markdown_documentation(
            source_files, doc_files, base_path,
            include_docs=True, include_source=False
        )
        
        assert "📖 Documentation:" in result
        assert "**🔧 Source Code Files:** 0 files (excluded)" in result
        assert "🔧 Source Code:" not in result


class TestVersionFunction:
    """Test version retrieval function"""
    
    def test_get_version_success(self):
        """Test successful version retrieval"""
        with patch("importlib.metadata.version", return_value="1.2.3"):
            version = get_version()
            assert version == "1.2.3"
    
    def test_get_version_failure(self):
        """Test version retrieval failure"""
        with patch("importlib.metadata.version", side_effect=Exception("Not found")):
            version = get_version()
            assert version == "unknown"


class TestCLIArguments:
    """Test CLI argument parsing"""
    
    def test_parse_args_default(self):
        """Test default argument parsing"""
        with patch("sys.argv", ["pocket-dump"]):
            parser = argparse.ArgumentParser()
            parser.add_argument("filename", nargs="?", help="Output filename")
            parser.add_argument("--source-only", action="store_true")
            parser.add_argument("--docs-only", action="store_true")
            
            args = parser.parse_args([])
            
            assert args.filename is None
            assert args.source_only is False
            assert args.docs_only is False
    
    def test_parse_args_with_filename(self):
        """Test parsing with filename argument"""
        parser = argparse.ArgumentParser()
        parser.add_argument("filename", nargs="?", help="Output filename")
        parser.add_argument("--source-only", action="store_true")
        parser.add_argument("--docs-only", action="store_true")
        
        args = parser.parse_args(["test.md"])
        
        assert args.filename == "test.md"
        assert args.source_only is False
        assert args.docs_only is False
    
    def test_parse_args_source_only(self):
        """Test parsing with --source-only flag"""
        parser = argparse.ArgumentParser()
        parser.add_argument("filename", nargs="?", help="Output filename")
        parser.add_argument("--source-only", action="store_true")
        parser.add_argument("--docs-only", action="store_true")
        
        args = parser.parse_args(["--source-only", "source.md"])
        
        assert args.filename == "source.md"
        assert args.source_only is True
        assert args.docs_only is False
    
    def test_parse_args_docs_only(self):
        """Test parsing with --docs-only flag"""
        parser = argparse.ArgumentParser()
        parser.add_argument("filename", nargs="?", help="Output filename")
        parser.add_argument("--source-only", action="store_true")
        parser.add_argument("--docs-only", action="store_true")
        
        args = parser.parse_args(["--docs-only"])
        
        assert args.filename is None
        assert args.source_only is False
        assert args.docs_only is True


class TestMainFunction:
    """Test the main CLI function end-to-end"""
    
    def test_main_with_valid_files(self, tmp_path, monkeypatch, capsys):
        """Test main function with valid file structure"""
        # Create test file structure
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        # Create source files
        (base_path / "__init__.py").write_text("# Init")
        (base_path / "agent.py").write_text("# Agent\nclass PocketAgent:\n    pass")
        
        # Create docs
        docs_path = base_path / "docs"
        docs_path.mkdir()
        (docs_path / "01_guide.md").write_text("# Guide\nWelcome!")
        
        # Change to temp directory for output
        monkeypatch.chdir(tmp_path)
        
        # Mock sys.argv
        test_args = ["pocket-dump", "test-output.md", "--base-path", str(base_path)]
        
        with patch("sys.argv", test_args):
            try:
                main()
            except SystemExit as e:
                # main() calls sys.exit(1) on error, we want success (no exception)
                pytest.fail(f"main() exited with error: {e}")
        
        # Check that output file was created
        output_file = tmp_path / "test-output.md"
        assert output_file.exists()
        
        # Check output content
        content = output_file.read_text()
        assert "Pocket Agent" in content
        assert "class PocketAgent:" in content
        assert "Welcome!" in content
        
        # Check console output
        captured = capsys.readouterr()
        assert "Complete dump generated successfully!" in captured.out
        assert "test-output.md" in captured.out
    
    def test_main_source_only(self, tmp_path, monkeypatch, capsys):
        """Test main function with --source-only flag"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        (base_path / "agent.py").write_text("# Agent code")
        
        monkeypatch.chdir(tmp_path)
        
        test_args = ["pocket-dump", "--source-only", "--base-path", str(base_path)]
        
        with patch("sys.argv", test_args):
            try:
                main()
            except SystemExit:
                pass  # Expected for some error cases
        
        captured = capsys.readouterr()
        assert "source only" in captured.out or "Generating" in captured.out
    
    def test_main_docs_only(self, tmp_path, monkeypatch, capsys):
        """Test main function with --docs-only flag"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        docs_path = base_path / "docs"
        docs_path.mkdir()
        (docs_path / "guide.md").write_text("# Documentation")
        
        monkeypatch.chdir(tmp_path)
        
        test_args = ["pocket-dump", "--docs-only", "--base-path", str(base_path)]
        
        with patch("sys.argv", test_args):
            try:
                main()
            except SystemExit:
                pass
        
        captured = capsys.readouterr()
        assert "docs only" in captured.out or "Generating" in captured.out
    
    def test_main_conflicting_flags(self, capsys):
        """Test main function with conflicting --source-only and --docs-only flags"""
        test_args = ["pocket-dump", "--source-only", "--docs-only"]
        
        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with error code 1
            assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "mutually exclusive" in captured.out
    
    def test_main_no_files_found(self, tmp_path, monkeypatch, capsys):
        """Test main function when no source files are found"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        
        monkeypatch.chdir(tmp_path)
        
        test_args = ["pocket-dump", "--base-path", str(empty_dir)]
        
        with patch("sys.argv", test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "No pocket agent source files found!" in captured.out
    
    def test_main_adds_md_extension(self, tmp_path, monkeypatch):
        """Test that main function adds .md extension when missing"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        (base_path / "__init__.py").write_text("# Init")
        
        monkeypatch.chdir(tmp_path)
        
        test_args = ["pocket-dump", "output", "--base-path", str(base_path)]
        
        with patch("sys.argv", test_args):
            try:
                main()
            except SystemExit:
                pass
        
        # Should create output.md, not output
        assert (tmp_path / "output.md").exists()
        assert not (tmp_path / "output").exists()


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_file_write_permission_error(self, tmp_path, monkeypatch, capsys):
        """Test handling of file write permission errors"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        (base_path / "__init__.py").write_text("# Init")
        
        monkeypatch.chdir(tmp_path)
        
        # Mock open to raise permission error
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")
            
            test_args = ["pocket-dump", "--base-path", str(base_path)]
            
            with patch("sys.argv", test_args):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "Dump failed:" in captured.out
    
    def test_unexpected_exception(self, tmp_path, monkeypatch, capsys):
        """Test handling of unexpected exceptions"""
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        (base_path / "__init__.py").write_text("# Init")
        
        monkeypatch.chdir(tmp_path)
        
        # Mock find_pocket_agent_files to raise an exception
        with patch("pocket_agent.pocket_dump.cli.find_pocket_agent_files") as mock_find:
            mock_find.side_effect = RuntimeError("Unexpected error")
            
            test_args = ["pocket-dump", "--base-path", str(base_path)]
            
            with patch("sys.argv", test_args):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                assert exc_info.value.code == 1
        
        captured = capsys.readouterr()
        assert "Dump failed:" in captured.out
        assert "Unexpected error" in captured.out


# Additional integration-style tests could go here
class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_full_workflow_realistic_structure(self, tmp_path, monkeypatch):
        """Test the full workflow with a realistic file structure"""
        # Create a realistic pocket_agent structure
        base_path = tmp_path / "pocket_agent"
        base_path.mkdir()
        
        # Core files
        (base_path / "__init__.py").write_text(
            'from .agent import PocketAgent\n'
            'from .client import PocketAgentClient\n'
            '__all__ = ["PocketAgent", "PocketAgentClient"]'
        )
        
        (base_path / "agent.py").write_text(
            '"""PocketAgent implementation"""\n'
            'class PocketAgent:\n'
            '    def __init__(self, config):\n'
            '        self.config = config\n'
            '\n'
            '    async def run(self):\n'
            '        return "completed"'
        )
        
        (base_path / "client.py").write_text(
            '"""PocketAgentClient implementation"""\n'
            'class PocketAgentClient:\n'
            '    def __init__(self, mcp_config):\n'
            '        self.mcp_config = mcp_config'
        )
        
        # Utils
        utils_path = base_path / "utils"
        utils_path.mkdir()
        (utils_path / "logger.py").write_text("# Logger implementation")
        (utils_path / "console_formatter.py").write_text("# Console formatter")
        
        # Documentation
        docs_path = base_path / "docs"
        docs_path.mkdir()
        
        (docs_path / "00_index.md").write_text(
            "# Pocket Agent Documentation\n"
            "Welcome to Pocket Agent framework documentation."
        )
        
        (docs_path / "01_getting-started.md").write_text(
            "# Getting Started\n"
            "This guide will help you get started with Pocket Agent."
        )
        
        # CLI
        cli_path = base_path / "pocket_dump"
        cli_path.mkdir()
        (cli_path / "cli.py").write_text("# CLI implementation")
        
        monkeypatch.chdir(tmp_path)
        
        # Run pocket-dump
        test_args = ["pocket-dump", "complete.md", "--base-path", str(base_path)]
        
        with patch("sys.argv", test_args):
            try:
                main()
            except SystemExit as e:
                if e.code != 0:
                    pytest.fail(f"Command failed with exit code {e.code}")
        
        # Verify output file
        output_file = tmp_path / "complete.md"
        assert output_file.exists()
        
        content = output_file.read_text()
        
        # Check structure
        assert "# 📖 Documentation:" in content
        assert "# 🔧 Source Code:" in content
        
        # Check documentation content
        assert "Welcome to Pocket Agent framework documentation." in content
        assert "This guide will help you get started" in content
        
        # Check source code content
        assert "class PocketAgent:" in content
        assert "class PocketAgentClient:" in content
        
        # Check metadata
        assert "pocket-dump" in content
