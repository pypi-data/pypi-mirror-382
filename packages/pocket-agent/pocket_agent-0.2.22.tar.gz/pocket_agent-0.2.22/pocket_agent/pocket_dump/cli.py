#!/usr/bin/env python3
"""
pocket-dump: A CLI tool to dump all Pocket Agent source code 
and documentation into a comprehensive markdown document.

Like a database dump, but for source code and docs! 📄
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Optional

def get_version():
    """Get version from package metadata"""
    try:
        from importlib.metadata import version
        return version("pocket-agent")
    except Exception:
        return "unknown"

def find_pocket_agent_files(base_path: Optional[Path] = None) -> List[Path]:
    """Find all pocket agent source files to include"""
    if base_path is None:
        # Try to find pocket_agent directory relative to this file
        base_path = Path(__file__).parent.parent  # Go up from pocket_dump to pocket_agent
        if not (base_path / "__init__.py").exists():
            # If running from installed package, look in the installed location
            import pocket_agent
            base_path = Path(pocket_agent.__file__).parent
    
    files = []
    
    # Core files
    core_files = [
        "__init__.py",
        "agent.py", 
        "client.py",
    ]
    
    # Utils files
    utils_files = [
        "utils/console_formatter.py",
        "utils/logger.py"
    ]
    
    # Check if files exist and add them
    for file_rel in core_files + utils_files:
        file_path = base_path / file_rel
        if file_path.exists():
            files.append(file_path)
        else:
            print(f"⚠️  Warning: {file_rel} not found at {file_path}")
    
    return files

def find_documentation_files(base_path: Optional[Path] = None) -> List[Path]:
    """Find documentation files in the package docs folder"""
    if base_path is None:
        # Try to find pocket_agent directory relative to this file
        base_path = Path(__file__).parent.parent  # Go up from pocket_dump to pocket_agent
        if not (base_path / "__init__.py").exists():
            # If running from installed package, look in the installed location
            import pocket_agent
            base_path = Path(pocket_agent.__file__).parent
    
    docs_path = base_path / "docs"
    if not docs_path.exists():
        return []
    
    doc_files = []
    
    # Get all markdown files in docs directory and sort them
    # This will handle the numbered structure (00_, 01_, etc.)
    md_files = sorted(docs_path.glob("*.md"))
    
    for doc_file in md_files:
        if doc_file.is_file():
            doc_files.append(doc_file)
    
    return doc_files

def read_file_safely(file_path: Path) -> str:
    """Read file content safely with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def count_lines_and_chars(content: str) -> tuple[int, int]:
    """Count lines and characters in content"""
    lines = len(content.split('\n'))
    chars = len(content)
    return lines, chars

def generate_markdown_documentation(source_files: List[Path], doc_files: List[Path], 
                                 base_path: Path, include_docs: bool = True, 
                                 include_source: bool = True) -> str:
    """Generate the complete markdown documentation"""
    
    total_files = len(source_files if include_source else []) + len(doc_files if include_docs else [])
    
    # Header
    mode_desc = "Complete Documentation & Source Code" if include_docs and include_source else (
        "Documentation" if include_docs else "Source Code"
    )
    
    content = f"""# {mode_desc} of Pocket Agent

**Pocket Agent Version:** v{get_version()}  
**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Files:** {total_files}

## 📋 Table of Contents

"""
    
    # Generate table of contents
    total_lines = 0
    total_chars = 0
    
    # Documentation section in TOC
    if include_docs and doc_files:
        content += "### 📖 Documentation\n\n"
        for file_path in doc_files:
            relative_path = file_path.relative_to(base_path)
            anchor = str(relative_path).lower().replace('/', '-').replace('.', '-').replace('_', '-')
            
            file_content = read_file_safely(file_path)
            lines, chars = count_lines_and_chars(file_content)
            total_lines += lines
            total_chars += chars
            
            # Create a friendly name for the TOC
            friendly_name = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            if file_path.stem.startswith(('00', '01', '02', '03', '04', '05', '06', '07', '08', '09')):
                friendly_name = friendly_name[2:].strip()  # Remove number prefix for display
            
            content += f"- 📖 [{friendly_name}](#{anchor}) *({lines:,} lines)*\n"
        content += "\n"
    
    # Source code section in TOC
    if include_source and source_files:
        content += "### 🔧 Source Code\n\n"
        for file_path in source_files:
            try:
                relative_path = file_path.relative_to(base_path)
            except ValueError:
                relative_path = Path("pocket_agent") / file_path.name
                
            anchor = str(relative_path).lower().replace('/', '-').replace('.', '-').replace('_', '-')
            
            file_content = read_file_safely(file_path)
            lines, chars = count_lines_and_chars(file_content)
            total_lines += lines
            total_chars += chars
            
            content += f"- 🔧 [{relative_path}](#{anchor}) *({lines:,} lines)*\n"
        content += "\n"
    
    content += f"**📊 Total Content:** {total_lines:,} lines, {total_chars:,} characters\n\n"
    content += "---\n\n"
    
    # Generate documentation section
    if include_docs and doc_files:
        content += "# 📖 Documentation:\n\n"
        
        for file_path in doc_files:
            relative_path = file_path.relative_to(base_path)
            file_content = read_file_safely(file_path)
            lines, chars = count_lines_and_chars(file_content)
            
            # Create friendly title
            friendly_name = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            if file_path.stem.startswith(('00', '01', '02', '03', '04', '05', '06', '07', '08', '09')):
                friendly_name = friendly_name[2:].strip()
            
            content += f"## 📖 {friendly_name}\n\n"
            content += f"**File:** `{relative_path}`  \n"
            content += f"**Stats:** {lines:,} lines, {chars:,} characters\n\n"
            
            # For markdown files, include the content directly (no code blocks)
            # This preserves the markdown formatting
            content += file_content
            content += "\n\n---\n\n"
    
    # Generate source code section
    if include_source and source_files:
        content += "# 🔧 Source Code:\n\n"
        
        for file_path in source_files:
            try:
                relative_path = file_path.relative_to(base_path)
            except ValueError:
                relative_path = Path("pocket_agent") / file_path.name
                
            file_content = read_file_safely(file_path)
            lines, chars = count_lines_and_chars(file_content)
            
            content += f"## 🔧 {relative_path}\n\n"
            content += f"**File Path:** `{relative_path}`  \n"
            content += f"**Stats:** {lines:,} lines, {chars:,} characters\n\n"
            
            # Add file description based on filename
            descriptions = {
                "__init__.py": "Package initialization and public API exports",
                "agent.py": "Core PocketAgent class - the heart of the framework with agent lifecycle management",
                "client.py": "PocketAgentClient for MCP server communication and tool execution",
                "console_formatter.py": "Console output formatting for agent events and interactions",
                "logger.py": "Professional logging configuration with file rotation and level management"
            }
            
            file_desc = descriptions.get(file_path.name, "Source code file")
            content += f"*{file_desc}*\n\n"
            
            # Syntax highlighting
            if file_path.suffix == '.py':
                content += "```python\n"
            else:
                content += "```\n"
            
            content += file_content
            content += "\n```\n\n"
            content += "---\n\n"
    
    # Footer with summary
    doc_count = len(doc_files) if include_docs else 0
    source_count = len(source_files) if include_source else 0
    
    content += f"""## 📊 Complete Dump Summary

### 📋 **Content Overview:**
- **📖 Documentation Files:** {doc_count} files{' ✓' if include_docs else ' (excluded)'}
- **🔧 Source Code Files:** {source_count} files{' ✓' if include_source else ' (excluded)'}
- **📏 Total Content:** {total_lines:,} lines ({total_chars:,} characters)

### 🏗️ **Framework Architecture:**
- **🤖 Core Agent (`agent.py`)** - Main orchestration and lifecycle management
- **🔌 Client Layer (`client.py`)** - MCP server communication and tool execution  
- **🛠️ Utilities** - Logging and console formatting for developer experience
- **📦 Public API (`__init__.py`)** - Clean, simple imports for end users
- **⚙️ CLI Tools** - Documentation and source code dumping utilities

### 🚀 **Key Features:**
- Multi-agent orchestration and sub-agent support
- Async/await throughout for performance
- Comprehensive error handling and logging
- Hook system for extensibility
- Clean separation of concerns
- Complete documentation and examples

---

*This complete dump was generated by `pocket-dump` - documentation and source code dumping utility.*

**Need another dump?** Run: `pocket-dump <filename>`  
**Just source?** Run: `pocket-dump --source-only <filename>`  
**Just docs?** Run: `pocket-dump --docs-only <filename>`
"""
    
    return content

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="pocket-dump",
        description="📄 Dump complete Pocket Agent documentation and source code into markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pocket-dump                        # Complete dump (docs + source)
  pocket-dump complete.md            # Custom filename
  pocket-dump --source-only          # Source code only
  pocket-dump --docs-only            # Documentation only
  
Like a database dump, but for docs and source code! 📄
        """
    )
    
    parser.add_argument(
        "filename",
        nargs="?",
        help="Output markdown filename (default: pocket-agent-dump.md)"
    )

    parser.add_argument(
        "--source-only",
        action="store_true",
        help="Only dump source code, no documentation"
    )

    parser.add_argument(
        "--docs-only",
        action="store_true",
        help="Only dump documentation, no source code"
    )
    
    parser.add_argument(
        "--base-path",
        type=Path,
        help="Base path to pocket_agent source (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    # Validate mutually exclusive flags
    if args.source_only and args.docs_only:
        print("❌ Error: --source-only and --docs-only are mutually exclusive")
        sys.exit(1)
    
    # Determine what to include
    include_docs = not args.source_only
    include_source = not args.docs_only
    
    # Determine output filename
    if args.source_only:
        default_name = "pocket-agent-source.md"
    elif args.docs_only:
        default_name = "pocket-agent-docs.md"
    else:
        default_name = "pocket-agent-dump.md"
        
    output_filename = args.filename or default_name
    
    # Ensure .md extension
    if not output_filename.endswith('.md'):
        output_filename += '.md'
    
    mode_desc = "docs + source" if include_docs and include_source else ("docs only" if include_docs else "source only")
    print(f"📄 Pocket Dump - Generating {mode_desc}...")
    print(f"📝 Output file: {output_filename}")
    
    try:
        # Find source files
        source_files = find_pocket_agent_files(args.base_path) if include_source else []
        
        # Find documentation files
        doc_files = find_documentation_files(args.base_path) if include_docs else []
        
        # Check that we found something
        if include_source and not source_files:
            print("❌ No pocket agent source files found!")
            print("   Make sure you're running this from a pocket-agent installation or source directory.")
            sys.exit(1)
            
        if include_docs and not doc_files:
            print("⚠️  Warning: No documentation files found in package docs folder")
            if args.docs_only:
                print("❌ Cannot proceed with --docs-only when no docs are found")
                sys.exit(1)
        
        total_files = len(source_files) + len(doc_files)
        print(f"📦 Found {len(doc_files)} doc files and {len(source_files)} source files...")
        
        # Determine base path
        if args.base_path:
            base_path = args.base_path
        elif source_files:
            base_path = source_files[0].parent if source_files[0].name == "__init__.py" else source_files[0].parent.parent
        elif doc_files:
            base_path = doc_files[0].parent.parent  # Go up from docs/ to package root
        else:
            base_path = Path.cwd()
        
        # Generate documentation
        markdown_content = generate_markdown_documentation(
            source_files, doc_files, base_path, include_docs, include_source
        )
        
        # Write output
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Success stats
        file_size = os.path.getsize(output_filename)
        if file_size < 1024:
            size_str = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        print(f"✅ Complete dump generated successfully!")
        print(f"📖 Documentation: {len(doc_files)} files")
        print(f"🔧 Source code: {len(source_files)} files")
        print(f"📊 Generated: {output_filename} ({size_str})")

        
    except Exception as e:
        print(f"❌ Dump failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
