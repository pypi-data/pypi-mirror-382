# FileAgent

## About

This repository is part of the SAND5G project, which aims to enhance security in 5G networks. FileAgent is a tool designed to facilitate the management of Snort rules in a containerized environment.

5G -and beyond- networks provide a strong foundation for EU’s digital transformation and are becoming one of the Union’s key assets to compete in the global market.

Securing 5G networks and the services running on top of them requires high quality technical security solutions and also strong collaboration at the operational level.

https://sand5g-project.eu

![SAND5G](https://sand5g-project.eu/wp-content/uploads/2024/06/SAND5G-logo-600x137.png)

## Overview

FileAgent is a Python-based application designed to accompany Snort in a containerized environment. It provides a FastAPI-based interface for uploading and managing custom rules for Snort. The application supports JSON and plain text file uploads, translates the content into Snort-compatible rules, and appends them to a rules file while ensuring backups and avoiding duplicates.

## Features

- Upload JSON or plain text files containing IP addresses or URLs.
- Automatically translate uploaded content into Snort-compatible rules.
- Append rules to a custom rules file (`mock.local.rules` by default).
- Backup the rules file before appending new rules.
- Avoid duplicate rule entries.

## Requirements

- Python 3.11 or higher
- Dependencies listed in `pyproject.toml`:
  - `fastapi`
  - `uvicorn`
  - `requests`
  - `python-multipart`

## Installation

### Clone from github

1. Clone the repository:

   ```bash
   git clone https://github.com/ISSG-Projects/FileAgentSAND5G.git
   cd FileAgentSAND5G
   ```

2. Create a virtual environment

   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install the required dependencies:

   ```bash
   pip install .
   ```

### pip install from github

```bash
pip install git+ssh://git@github.com/ISSG-Projects/FileAgentSAND5G.git
```

## API Endpoints

- POST /upload: Upload a JSON or plain text file containing IP addresses or URLs. The content is translated into Snort rules and appended to the rules file.

## Documentation

The project documentation is generated using pdoc3. To generate and view the documentation:

Open the generated HTML files in the `docs` directory.

More information at [docs/pdoc/README.md](docs/pdoc/README.md).

Additionally the FastAPI framework provides an interactive API documentation at `http://localhost:8000/docs` when the application is running. This allows you to test the API endpoints directly from your browser.

## Future Implementations

<input disabled="" type="checkbox"> Add support for additional file formats (e.g., XML, CSV).
<input disabled="" type="checkbox"> Implement rule validation against a predefined schema.
<input disabled="" type="checkbox"> Add logging for better traceability.
<input disabled="" type="checkbox"> Create a web-based dashboard for managing rules.
<input disabled="" type="checkbox"> Integrate with external threat intelligence feeds.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes
