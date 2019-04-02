# es-responder [![Picture](https://raw.github.com/janelia-flyem/janelia-flyem.github.com/master/images/HHMI_Janelia_Color_Alternate_180x40.png)](http://www.janelia.org)

[![Build Status](https://travis-ci.org/JaneliaSciComp/es-responder.svg?branch=master)](https://travis-ci.org/JaneliaSciComp/es-responder)
[![GitHub last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/JaneliaSciComp/es-responder)
[![GitHub commit merge status](https://img.shields.io/github/commit-status/badges/shields/master/5d4ab86b1b5ddfb3c4a70a70bd19932c52603b8c.svg)](https://github.com/JaneliaSciComp/es-responder)

Lightweight custom REST API for ElasticSearch queries

## Deployment

After installing on the production server, take the following steps to start the system:
1. `cd /opt/flask/es-responder`
1. `sudo systemctl gunicorn start`
1. `sudo systemctl nginx start`

## Development
1. Create and activate a clean Python 3 environment:
    ```python3 -m venv myenv
    source myenv/bin/activate```
1. Install dependencies:
    `pip3 install -r requirements.txt`
1. Run tests:
    `python3 test_base.py`
1. Start server:
    `python3 es_responder.py`
1. When you're done, deactivate the virtual environment:
    `deactivate`

