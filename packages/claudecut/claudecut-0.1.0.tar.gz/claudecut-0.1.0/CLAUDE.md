## Core Development Rules

1. **Package Management**: ONLY use uv (`uv add package`, `uv run tool`)
2. **Code Quality**: Type hints required, use pyrefly (`pyrefly init`, `pyrefly check`)
3. **Testing**: `uv run pytest`, async by default
4. **Style**: PEP8, f-strings

## Development Philosophy
- **Simplicity**: Write simple, readable code
- **Less Code = Less Debt**: Minimize footprint
- **Build Iteratively**: Start minimal, verify, then add complexity
- **Dont' Write Tests**: Unless I specifically ask you to do so

## Best Practices
- Early returns, descriptive names, DRY code
- Functional style when clear
- Run tests frequently with realistic inputs
- TODO comments for issues

## Tools
- Use pydantic for objects, SQLModel for DB entities
- SQLite for dev, PostgreSQL if needed
- Use context7 mcp tool to fetch up-to-date code library documentation

## Other rules
- Never update README.md unless I specifically ask you to
