# es-responder [![Picture](https://raw.github.com/janelia-flyem/janelia-flyem.github.com/master/images/HHMI_Janelia_Color_Alternate_180x40.png)](http://www.janelia.org)

[![Build Status](https://travis-ci.org/JaneliaSciComp/es-responder.svg?branch=master)](https://travis-ci.org/JaneliaSciComp/es-responder)
[![GitHub last commit](https://img.shields.io/github/last-commit/google/skia.svg)](https://github.com/JaneliaSciComp/es-responder)
[![GitHub commit merge status](https://img.shields.io/github/commit-status/badges/shields/master/5d4ab86b1b5ddfb3c4a70a70bd19932c52603b8c.svg)](https://github.com/JaneliaSciComp/es-responder)
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Requirements Status](https://requires.io/github/JaneliaSciComp/es-responder/requirements.svg?branch=master)](https://requires.io/github/connectome-neuprint/JaneliaSciComp/es-responder/requirements/?branch=master)

## Summary
A lightweight custom REST API for ElasticSearch queries. Once installed, just going to the top-level page will show Swagger documentation.

## Configuration

This system depends on the [Centralized Config](https://github.com/JaneliaSciComp/Centralized_Config) system, and
will use the following configurations:
- rest_services
- servers
- elasticsearch_queries

The location of the configuration system is in the config.cfg file as CONFIG_ROOT.

## Deployment

After installing on the production server, take the following steps to start the system:
```
cd /opt/flask/es-responder
sudo systemctl start gunicorn
sudo systemctl start nginx
```

## Development
1. Create and activate a clean Python 3 environment:
    ```
    python3 -m venv myenv
    source myenv/bin/activate
    ```
1. Install dependencies:

    `pip3 install -r requirements.txt`
1. Run tests:

    `python3 test_base.py`
1. Start server:

    `python3 es_responder.py`
1. When you're done, deactivate the virtual environment:

    `deactivate`
