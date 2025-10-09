# Project Structure

This document outlines the organizational patterns for this codebase.

## Directory Organization
Update this structure as the project develops:

```
.
├── README.md      # A descriptive overview of the project, it's functionality and the development process with links to any other markdown documentation in the project.
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
├── config/        # Configuration files
└── .kiro/         # Kiro AI assistant configuration
    └── steering/  # AI guidance documents
```

## File Naming Conventions
- Use consistent naming patterns within each language/framework
- Prefer descriptive names over abbreviations
- Follow language-specific conventions (camelCase, snake_case, etc.)

## Code Organization
- Group related functionality together
- Separate concerns appropriately
- Keep file sizes manageable
- Use clear module/package boundaries

## Configuration Files
- Keep configuration at the project root when possible
- Use environment-specific configs when needed
- Document any non-standard configuration choices

## Documentation
- README.md at project root with setup instructions
- Inline code comments for complex logic
- API documentation for public interfaces
- Architecture decisions in docs/ folder when significant