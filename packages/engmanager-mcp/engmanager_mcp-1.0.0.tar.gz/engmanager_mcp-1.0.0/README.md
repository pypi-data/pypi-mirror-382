# Engineering Manager MCP

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![PyPI](https://img.shields.io/pypi/v/engmanager-mcp)](https://pypi.org/project/engmanager-mcp/)
[![uvx](https://img.shields.io/badge/uvx-compatible-orange.svg)](https://github.com/astral-sh/uvx)

An MCP (Model Context Protocol) server that provides LLMs with structured workflow guidance and "next step" instructions for development procedures. Perfect for maintaining consistent development practices across projects without having to repeatedly explain procedures to AI assistants.

This project welcomes contributions from AI/LLM agents! **Pull requests from Claude, GPT, and other AI models are actively encouraged.**

**Guidelines for AI contributors:**
- Follow existing code patterns and documentation standards
- Include comprehensive commit messages explaining changes
- Test changes thoroughly before submitting PRs
- Update documentation when adding new features

## 🎯 Purpose

Engineering Manager MCP solves a common problem: **LLMs forget your development procedures.** Instead of repeatedly reminding your AI assistant about branch naming conventions, commit message formats, PR templates, or deployment steps, let Engineering Manager MCP provide that guidance on demand.

**Use Cases:**
- 🔄 **Consistent Workflows** - Maintain standardized development procedures across projects
- 📋 **Step-by-Step Guidance** - LLMs can query "what's next?" at any point in the workflow
- 🎯 **Context-Aware Suggestions** - Returns relevant workflow sections based on current task
- 🔧 **Multi-Project Support** - Different procedures for different projects
- 📝 **Template Variables** - Customize procedures with project-specific values

## ✨ Quick Start

### Installation from PyPI

```bash
# Run directly with uvx (recommended)
uvx engmanager-mcp

# Or install with pip
pip install engmanager-mcp
```

### Configure in Claude Code

For project-specific configuration, add to your local `.mcp.json` in the project directory, or add to your global `claude_code_config.json`:

```json
{
  "mcpServers": {
    "engmanager": {
      "command": "uvx",
      "args": ["engmanager-mcp"],
      "env": {
        "ENGMANAGER_DEFAULT_PROJECT": "myproject"
      }
    }
  }
}
```

### Create Your First Project

1. **Create a project configuration:**

```bash
mkdir -p ~/.config/engmanager-mcp
cat > ~/.config/engmanager-mcp/myproject-config.json <<EOF
{
  "project_name": "myproject",
  "procedure_file": "myproject-workflow.md",
  "variables": {
    "REPO_OWNER": "yourname",
    "REPO_NAME": "myproject",
    "DEFAULT_BRANCH": "main"
  }
}
EOF
```

2. **Create a workflow procedure:**

```bash
cat > ~/.config/engmanager-mcp/myproject-workflow.md <<EOF
# My Project Workflow

## 1. Branch Creation

Create a feature branch:
\`\`\`bash
git checkout -b feature/my-feature
\`\`\`

## 2. Development

Make your changes and commit:
\`\`\`bash
git add .
git commit -m "feat: description"
\`\`\`

## 3. Push & PR

Push and create a pull request:
\`\`\`bash
git push -u origin feature/my-feature
gh pr create --title "feat: Description"
\`\`\`
EOF
```

3. **Use in Claude:**

```
You: "What's the first step in the workflow?"
Claude: [calls get_next_step tool]
Engineering Manager MCP: Returns "Step 1: Branch Creation..."

You: "What's next?"
Claude: [calls get_next_step with current_step=1]
Engineering Manager MCP: Returns "Step 2: Development..."
```

## 🔧 Available Tools

### `get_next_step`
Get the next step in the workflow.

```python
get_next_step(project="myproject", current_step=1)
```

**Parameters:**
- `project` (optional): Project name (uses default if not specified)
- `current_step` (optional): Current step number (defaults to 0 for first step)

### `get_workflow_section`
Get a specific section from the workflow by name.

```python
get_workflow_section(section="Error Recovery Protocols", project="myproject")
```

### `list_workflow_steps`
Get an overview of all numbered steps.

```python
list_workflow_steps(project="myproject")
```

### `list_available_projects`
List all configured projects.

```python
list_available_projects()
```

### `get_project_info`
Get detailed information about a project's configuration.

```python
get_project_info(project="myproject")
```

## 📚 Available Resources

### `engmanager://procedures/{project}`
Get the full procedure file with variables substituted.

### `engmanager://config/{project}`
Get the project configuration.

### `engmanager://templates`
Get documentation about template variables.

### `engmanager://projects`
List all available projects with status.

## 🎨 Template Variables

Procedures support template variables for customization:

```markdown
## Branch Creation for {PROJECT_NAME}

Create a branch:
\`\`\`bash
git checkout -b feature/my-feature
git push -u origin feature/my-feature
\`\`\`

Your repository: {REPO_OWNER}/{REPO_NAME}
Default branch: {DEFAULT_BRANCH}
```

**Common Variables:**
- `{PROJECT_NAME}` - Project name
- `{REPO_OWNER}` - GitHub repository owner
- `{REPO_NAME}` - GitHub repository name
- `{DEFAULT_BRANCH}` - Default branch (main/master)
- `{ISSUE_NUMBER}` - Current issue number
- `{BRANCH_PREFIX}` - Branch prefix (feature/fix/refactor)

Define custom variables in your project's config file.

## 📁 Project Structure

```
~/.config/engmanager-mcp/
├── myproject-config.json       # Project configuration
├── myproject-workflow.md       # Workflow procedure
├── another-project-config.json
└── another-project-workflow.md
```

**Alternative locations:**
- `./procedures/` (relative to current directory)
- `~/.config/engmanager-mcp/` (user config)
- `/etc/engmanager-mcp/` (system-wide)

## ⚙️ Configuration

### Environment Variables

- `ENGMANAGER_DEFAULT_PROJECT` - Default project name
- `ENGMANAGER_MCP_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `ENGMANAGER_PROCEDURES_DIR` - Custom procedures directory
- `ENGMANAGER_MCP_TRANSPORT` - Transport mode (stdio or http)

### Project Configuration Format

```json
{
  "project_name": "myproject",
  "procedure_file": "myproject-workflow.md",
  "variables": {
    "REPO_OWNER": "username",
    "REPO_NAME": "repository",
    "DEFAULT_BRANCH": "main",
    "CUSTOM_VAR": "custom_value"
  }
}
```

**Required Fields:**
- `project_name` - Unique project identifier
- `procedure_file` - Filename of the markdown procedure

**Optional Fields:**
- `variables` - Dictionary of template variables

## 📖 Example Use Cases

### Use Case 1: Consistent Git Workflow

**Problem:** Different team members follow different git workflows.

**Solution:** Create a standardized procedure that LLMs can reference:

```markdown
## 1. Branch Creation
- Always create from main
- Use conventional naming: feature/fix/refactor
- Format: <type>/<description>-issue-<number>

## 2. Commit Messages
- Use conventional commits format
- Include issue reference
- Add "Resolves #N" for auto-close
```

LLMs can now query these steps and follow them consistently.

### Use Case 2: Multi-Project Development

**Problem:** Working on multiple projects with different procedures.

**Solution:** Configure multiple projects:

```bash
~/.config/engmanager-mcp/
├── frontend-config.json
├── frontend-workflow.md
├── backend-config.json
└── backend-workflow.md
```

LLMs can switch between project contexts easily.

### Use Case 3: Onboarding Documentation

**Problem:** New team members (including AI assistants) need workflow guidance.

**Solution:** Comprehensive procedure files serve as executable documentation:

```markdown
## Developer Setup
1. Clone repository
2. Install dependencies
3. Configure environment
4. Run development server

## Development Workflow
[Steps...]

## Deployment Process
[Steps...]

## Error Recovery
[Procedures...]
```

## 🔨 Development Setup

### Local Installation

```bash
# Clone repository
git clone https://github.com/scarr7981/engmanager-mcp.git
cd engmanager-mcp

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install in editable mode for development
pip install -e .

# Run locally
python -m engmanager_mcp.server
# or
engmanager-mcp
```

### Development Mode with Claude Code

For local development and testing with Claude Code, add this to your project's `.mcp.json` file:

```json
{
  "mcpServers": {
    "engmanager": {
      "command": "/absolute/path/to/engmanager-mcp/.venv/bin/python",
      "args": ["-m", "engmanager_mcp.server"],
      "cwd": "/absolute/path/to/engmanager-mcp",
      "env": {
        "ENGMANAGER_DEFAULT_PROJECT": "example",
        "ENGMANAGER_MCP_LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

**Important:**
- Replace `/absolute/path/to/engmanager-mcp` with the actual path to your cloned repository
- For Windows WSL, use: `/mnt/c/Users/username/path/to/engmanager-mcp/.venv/bin/python`
- For Windows native, use: `C:\\absolute\\path\\to\\engmanager-mcp\\.venv\\Scripts\\python.exe`
- The `.mcp.json` file should be in the project root directory
- This file is gitignored, so your local config won't be committed

This configuration:
- Uses the virtual environment's Python interpreter directly
- Runs from your local development directory
- Enables DEBUG logging for troubleshooting
- Sets the example project as default
- Allows you to edit code and see changes immediately (restart Claude Code to reload)

### Testing

Create a test project:

```bash
mkdir -p procedures
cat > procedures/test-config.json <<EOF
{
  "project_name": "test",
  "procedure_file": "example-workflow.md",
  "variables": {
    "REPO_OWNER": "testuser",
    "REPO_NAME": "testrepo",
    "DEFAULT_BRANCH": "main"
  }
}
EOF

# Copy example workflow
cp procedures/example-workflow.md procedures/test-workflow.md

# Test with MCP inspector or Claude Code
```

## 📦 Publishing to PyPI

### Build Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check distribution
twine check dist/*
```

### Upload to PyPI

```bash
# Upload to Test PyPI first
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ engmanager-mcp

# Upload to PyPI
twine upload dist/*
```

### Using GitHub Actions

This project can be configured with GitHub Actions for automatic PyPI publishing on tagged releases. See `cargoshipper-mcp` for reference.

## 🤝 Contributing

This project is inspired by the EXAMPLE_PROCEDURE.md workflow for Trowel.io and follows similar patterns.

**Contribution Guidelines:**
- Follow existing code patterns
- Add comprehensive docstrings
- Update README for new features
- Test with real procedures
- Include example configurations

## 📄 License

MIT License - See LICENSE file for details

## 🔗 Related Projects

- [CargoShipper MCP](https://github.com/scarr7981/cargoshipper-mcp) - Infrastructure automation MCP server
- [Model Context Protocol](https://modelcontextprotocol.io/) - Official MCP documentation
- [FastMCP](https://github.com/jlowin/fastmcp) - Python MCP framework

## 💡 Tips & Best Practices

### Writing Effective Procedures

1. **Use numbered steps** for sequential workflows
2. **Include code examples** in bash blocks
3. **Document error recovery** procedures
4. **Add quality gates** at key checkpoints
5. **Use template variables** for project-specific values

### Organizing Projects

1. **One config per project** - Keep projects isolated
2. **Shared procedures** - Reference common workflows
3. **Default project** - Set for most common use case
4. **Version control** - Keep procedures in git

### LLM Integration

1. **Ask "what's next?"** - Simple queries work best
2. **Provide context** - Mention current step if known
3. **Query sections** - Jump to specific workflow parts
4. **List steps** - Get overview before starting

## 🐛 Troubleshooting

### "Project not found"

- Check config file location
- Verify filename format: `<project>-config.json`
- Check `ENGMANAGER_DEFAULT_PROJECT` environment variable

### "Procedure file not found"

- Verify `procedure_file` path in config
- Check procedures directory
- Ensure markdown file exists

### "Missing template variables"

- Check procedure file for `{VARIABLE}` syntax
- Add missing variables to config `variables` object
- Variables must be UPPERCASE with underscores

### "No projects configured"

- Add at least one `<project>-config.json` file
- Check config search paths
- Verify JSON syntax in config files

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/scarr7981/engmanager-mcp/issues)
- **Documentation**: [GitHub README](https://github.com/scarr7981/engmanager-mcp)
- **MCP Help**: [Model Context Protocol Docs](https://modelcontextprotocol.io/)

---

**Made with ❤️ for better AI-assisted development workflows**
