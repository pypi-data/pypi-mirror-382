# Development Guide

This document provides instructions for developers who want to contribute to the `checksum_dict` project or understand its build process.

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.7 or later
- Cython
- setuptools
- setuptools_scm

## Setting Up the Development Environment

1. **Clone the Repository**

   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/BobTheBuidler/checksum_dict.git
   cd checksum_dict
   ```

2. **Install Dependencies**

   Install the required Python packages:

   ```bash
   pip install cchecksum
   ```

3. **Build the Cython Extensions**

   The project uses Cython to compile `.pyx` files. To build the extensions, run:

   ```bash
   python setup.py build_ext --inplace
   ```

## Versioning

The project uses `setuptools_scm` for versioning. This tool automatically manages the version number based on your Git tags. Ensure your repository is tagged correctly to reflect the version changes.

## Running Tests

To run the tests, you can use a testing framework like `pytest`. Install it if you haven't already:

```bash
pip install pytest
```

Then, run the tests:

```bash
pytest
```

## Contributing

We welcome contributions! Please fork the repository and submit a pull request with your changes. Ensure your code follows the project's coding standards and includes appropriate tests.

## Additional Notes

- The `setup.py` file is configured to include package data and compile Cython files with specific compiler directives.
- The project is not zip-safe due to the use of Cython extensions.

For any questions or further assistance, feel free to open an issue on the GitHub repository.