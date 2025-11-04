# Contributing to Cloudburst Management System

Thank you for your interest in contributing to the Cloudburst Management System! This document provides guidelines for contributing to this academic DBMS project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Database Guidelines](#database-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This is an academic project focused on learning and collaboration. Please:
- Be respectful and constructive in discussions
- Help others learn and understand concepts
- Share knowledge about database management and Python development
- Focus on improving the educational value of the project

## Getting Started

1. **Fork the Repository**
   ```bash
   # Click the 'Fork' button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/cloudburst_management.git
   cd cloudburst_management
   ```

3. **Add Upstream Remote**
   ```bash
   git remote add upstream https://github.com/mahad2810/cloudburst_management.git
   ```

## Development Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Database**
   ```bash
   mysql -u root -p < database_schema.sql
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## How to Contribute

### Reporting Bugs
- Check if the bug has already been reported in Issues
- Create a new issue with detailed description
- Include steps to reproduce, expected vs actual behavior
- Add relevant screenshots or error messages

### Suggesting Features
- Open an issue with the `enhancement` label
- Explain the feature and its educational value
- Discuss implementation approach
- Consider database design implications

### Code Contributions

**Good First Issues:**
- Improve documentation or docstrings
- Add data validation
- Create new SQL queries
- Enhance visualizations
- Add unit tests
- Improve error handling

**Areas for Contribution:**
- Database query optimization
- New dashboard features
- Additional data analytics
- UI/UX improvements
- Testing and validation
- Performance enhancements

## Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Comment complex logic

**Example:**
```python
def calculate_risk_level(rainfall_mm: float, population: int) -> str:
    """
    Calculate risk level based on rainfall and population.
    
    Args:
        rainfall_mm: Rainfall amount in millimeters
        population: Population of the affected region
    
    Returns:
        str: Risk level ('Low', 'Medium', 'High', 'Critical')
    """
    if rainfall_mm > 100 and population > 100000:
        return 'Critical'
    # ... rest of logic
```

### SQL Guidelines
- Use uppercase for SQL keywords
- Properly indent complex queries
- Add comments explaining complex joins
- Use meaningful table and column aliases
- Index frequently queried columns

**Example:**
```sql
-- Get regions with highest rainfall in last 7 days
SELECT 
    r.region_name,
    AVG(rd.rainfall_mm) AS avg_rainfall,
    COUNT(*) AS data_points
FROM affected_regions r
INNER JOIN rainfall_data rd ON r.region_name = rd.region
WHERE rd.date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY r.region_name
ORDER BY avg_rainfall DESC
LIMIT 10;
```

## Database Guidelines

### Schema Changes
- Document all schema changes in `database_schema.sql`
- Include migration scripts if needed
- Update sample data accordingly
- Test with existing data

### Query Optimization
- Use EXPLAIN to analyze query performance
- Add appropriate indexes
- Avoid SELECT *
- Use JOINs efficiently
- Consider query result caching

### Data Integrity
- Maintain referential integrity
- Use appropriate constraints
- Validate data before insertion
- Handle NULL values properly

## Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, documented code
   - Follow coding standards
   - Test your changes thoroughly

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of changes"
   ```
   
   **Commit Message Format:**
   - `Add:` New feature or functionality
   - `Fix:` Bug fix
   - `Update:` Modify existing feature
   - `Refactor:` Code restructuring
   - `Docs:` Documentation changes
   - `Test:` Add or update tests

4. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Provide clear description
   - Reference related issues
   - Add screenshots if applicable

6. **Code Review**
   - Address reviewer comments
   - Make requested changes
   - Update your PR

7. **Merge**
   - Once approved, your PR will be merged
   - Delete your feature branch

## Testing

Before submitting a PR, ensure:
- [ ] Code runs without errors
- [ ] Database queries execute successfully
- [ ] All pages load correctly
- [ ] No sensitive data in commits
- [ ] Documentation is updated
- [ ] .env file not included

## Questions?

Feel free to:
- Open an issue for discussion
- Ask questions in existing issues
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Project documentation
- Release notes

Thank you for contributing to this educational project! 🎓🌧️
