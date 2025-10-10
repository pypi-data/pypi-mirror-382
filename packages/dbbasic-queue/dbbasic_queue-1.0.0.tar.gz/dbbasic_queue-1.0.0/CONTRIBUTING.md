# Contributing to dbbasic-queue

Thank you for your interest in contributing to dbbasic-queue!

## Philosophy

dbbasic-queue follows the DBBasic philosophy:

- **Tiny**: Keep the core under 500 lines
- **Simple**: TSV files, no complex dependencies
- **Readable**: Code you can understand and modify
- **Unix-Compatible**: Works with standard Unix tools

## Development Setup

```bash
# Clone the repository
git clone https://github.com/dbbasic/dbbasic-queue
cd dbbasic-queue

# Install in development mode
pip install -e .

# Run tests
python3 tests/test_queue.py

# Run demo
python3 demo.py
```

## Code Style

- Follow PEP 8
- Keep functions small and focused
- Add docstrings for all public functions
- Use type hints where helpful

## Testing

All changes should include tests:

```bash
# Run test suite
python3 tests/test_queue.py

# Or with pytest
pytest tests/test_queue.py -v
```

## Submitting Changes

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## Areas for Contribution

- Additional examples
- Documentation improvements
- Performance optimizations
- Bug fixes
- Test coverage

## Questions?

Open an issue on GitHub or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
