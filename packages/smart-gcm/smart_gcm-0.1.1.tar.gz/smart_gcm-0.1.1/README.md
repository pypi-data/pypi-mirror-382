# Smart Commit

AI-powered Git commit message generator that follows the Conventional Commits specification using Google Gemini API.

## Features

- Generates commit messages using Google Gemini AI
- Follows Conventional Commits 1.0.0 specification
- Interactive editing with Vim
- Regenerate messages on demand
- Supports all conventional commit types

## Installation

### From PyPI (once published)

```bash
pip install smart-gcm
```

### From Source

```bash
git clone https://github.com/aakashvarma/smart-gcm.git
cd smart-gcm
pip install -e .
```

## Prerequisites

- Python 3.6 or higher
- Git
- Vim
- Google Gemini API key

## Setup

1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. Set the environment variable:

```bash
# Linux/Mac
export GEMINI_API_KEY="your-api-key-here"

# Windows
set GEMINI_API_KEY=your-api-key-here
```

For permanent setup, add to your shell profile:

```bash
# Bash (~/.bashrc or ~/.bash_profile)
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc

# Zsh (~/.zshrc)
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
```

## Usage

1. Stage your changes:

```bash
git add <files>
```

2. Run Smart Commit:

```bash
gcm
```

3. Follow the interactive prompts:
   - Select commit type (feat, fix, refactor, style, test, docs, build, ops, chore, revert)
   - Enter optional scope (max 20 characters)
   - Review the AI-generated commit message

4. Choose an action:
   - `a` - Accept and commit
   - `e` - Edit in Vim
   - `r` - Regenerate message
   - `c` - Cancel

## Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **refactor**: Code refactoring (including performance improvements)
- **style**: Code style changes (formatting, semicolons, etc.)
- **test**: Adding or updating tests
- **docs**: Documentation changes
- **build**: Build system or dependency changes
- **ops**: Operational/infrastructure changes
- **chore**: Maintenance tasks
- **revert**: Revert previous commit

## Examples

```bash
# Feature with scope
feat(auth): add OAuth2 login support
- Implement Google OAuth2 integration
- Add user session management

# Bug fix
fix(api): resolve null pointer exception in user endpoint
- Add null check for user object
- Update error handling

# Breaking change
feat(api)!: change response format to JSON:API spec
BREAKING CHANGE: all API responses now follow JSON:API specification
```

## Development

### Project Structure

```
smart-gcm/
├── smart_commit/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── commit.py       # Commit message generation
│   └── utils.py        # Utility functions
├── setup.py
├── README.md
├── LICENSE
└── .gitignore
```

### Running from Source

```bash
python -m smart_commit.cli
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any issues or have questions, please file an issue on [GitHub](https://github.com/aakashvarma/smart-gcm/issues).