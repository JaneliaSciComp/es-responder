import os
import requests
import sys
from datetime import datetime, timedelta
import elasticsearch
from time import time
from urllib.parse import parse_qs
from flask import Flask, g, render_template, request, jsonify
from flask_cors import CORS
from flask_swagger import swagger


__version__ = '0.1.0'
app = Flask(__name__)
app.config.from_pyfile("config.cfg")
CORS(app)
app.config['STARTTIME'] = time()
app.config['STARTDT'] = datetime.now()
start_time = ''
# Configuration
CONFIG = {'config': {'url': 'http://config.int.janelia.org/'}}
QUERY = {}
SERVER = {}
esearch = ''

# *****************************************************************************
# * Classes                                                                   *
# *****************************************************************************


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        retval = dict(self.payload or ())
        retval['rest'] = {'error': self.message}
        return retval

# *****************************************************************************
# * Flask                                                                     *
# *****************************************************************************


@app.before_request
def before_request():
    global esearch,start_time, CONFIG, QUERY, SERVER
    start_time = time()
    app.config['COUNTER'] += 1
    endpoint = request.endpoint if request.endpoint else '(Unknown)'
    app.config['ENDPOINTS'][endpoint] = app.config['ENDPOINTS'].get(endpoint, 0) + 1
    if request.method == 'OPTIONS':
        result = initializeResult()
        return generateResponse(result)
    if not len(QUERY):
        data = call_responder('config', 'config/rest_services')
        CONFIG = data['config']
        data = call_responder('config', 'config/servers')
        SERVER = data['config']
        data = call_responder('config', 'config/elasticsearch_queries')
        QUERY = data['config']
    if not esearch:
        try:
            esearch = elasticsearch.Elasticsearch(SERVER['elk-elastic']['address'])
        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
            sys.exit(-1)


# ******************************************************************************
# * Utility functions                                                          *
# ******************************************************************************


def get_parameters(result):
    pd = dict()
    if request.query_string:
        query_string = request.query_string
        if type(query_string) is not str:
            query_string = query_string.decode('utf-8')
        result['rest']['query_string'] = query_string
        qs = parse_qs(query_string)
        for key,val in qs.items():
            pd[key] = val[0]
    elif request.form:
        result['rest']['form'] = request.form
        for i in request.form:
            pd[i] = request.form[i]
    elif request.json:
        result['rest']['json'] = request.json
        pd = request.json
    elif request.headers:
        for i in request.headers:
            if '-' in i[0] or i[0].lower() in ['accept', 'host', 'connection']:
                continue
            pd[i[0].lower()] = i[1]
        result['rest']['headers'] = pd 
    return(pd)


def initializeResult():
    result = {"rest": {'requester': request.remote_addr,
                       'url': request.url,
                       'endpoint': request.endpoint,
                       'error': False,
                       'elapsed_time': ''}}
    return result


def call_responder(server, endpoint):
    url = CONFIG[server]['url'] + endpoint
    try:
        req = requests.get(url)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(-1)
    if req.status_code == 200:
        return req.json()
    sys.exit(-1)


def generateResponse(result):
    global start_time
    result['rest']['elapsed_time'] = str(timedelta(seconds=(time() - start_time)))
    return jsonify(**result)


# *****************************************************************************
# * Endpoints                                                                 *
# *****************************************************************************


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def showSwagger():
    return render_template('swagger_ui.html')


@app.route("/spec")
def spec():
    return getDocJson()


@app.route('/doc')
def getDocJson():
    swag = swagger(app)
    swag['info']['version'] = __version__
    swag['info']['title'] = "ElasticSearch Responder"
    return jsonify(swag)


@app.route("/stats")
def stats():
    '''
    Return stats
    Return uptime/requests statistics.
    ---
    tags:
      - Diagnostics
    responses:
      200:
          description: Stats
      400:
          description: Stats could not be calculated
    '''
    result = initializeResult()
    try:
        start = datetime.fromtimestamp(app.config['STARTTIME']).strftime('%Y-%m-%d %H:%M:%S')
        up_time = datetime.now() - app.config['STARTDT']
        health = esearch.cluster.health()
        result['stats'] = {"version": __version__,
                           "requests": app.config['COUNTER'],
                           "start_time": start,
                           "uptime": str(up_time),
                           "health": health,
                           "python": sys.version,
                           "pid": os.getpid(),
                           "endpoint_counts": app.config['ENDPOINTS']
                           }
        if None in result['stats']['endpoint_counts']:
            del result['stats']['endpoint_counts']
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        raise InvalidUsage('Error: %s' % (message,))
    return generateResponse(result)


# *****************************************************************************
# * DVID endpoints                                                            *
# *****************************************************************************
@app.route('/dvid_hitcount', methods=['GET'])
def dvid_hitcount_minute():
    '''
    Number of ES DVID hits in the last minute
    Return the total number of hits over the last minute for all 
    instrumented DVID servers.
    ---
    tags:
      - DVID
    responses:
      200:
          description: query response
    '''
    result = initializeResult()
    index = "emdata*_dvid_activity-*"
    payload = {"query": {"range": {"@timestamp": {"gte": "now-1m"}}}}
    result['rest']['payload'] = payload
    try:
        es_result = esearch.search(index=index, body=payload,
                                   filter_path=['hits.total'])
    except Exception as ex:
        raise InvalidUsage(str(ex))
    result['result'] = es_result['hits']['total']
    return generateResponse(result)


@app.route('/dvid_hitcount/<string:period>', methods=['GET'])
def dvid_hitcount(period):
    '''
    Return the total number of ES DVID hits over the last specified 
    time period for all instrumented DVID servers.
    ---
    tags:
      - DVID
    parameters:
      - in: path
        name: period
        type: string
        required: true
        description: time period (1s, 5m, 1h, 7d, etc.)
    responses:
      200:
          description: query response
    '''
    result = initializeResult()
    index = "emdata*_dvid_activity-*"
    payload = {"query": {"range": {"@timestamp": {"gte": "now-" + period}}}}
    result['rest']['payload'] = payload
    try:
        es_result = esearch.search(index=index, body=payload,
                                   filter_path=['hits.total'])
    except Exception as ex:
        raise InvalidUsage(str(ex))
    result['result'] = es_result['hits']['total']
    return generateResponse(result)


# *****************************************************************************
# * General endpoints                                                         *
# *****************************************************************************
@app.route('/query/<string:query>', methods=['GET'])
def query(query):
    '''
    Execute a general query
    Return results for a general query as defined in the 
    elasticsearch_queries configuration.
    ---
    tags:
      - General
    parameters:
      - in: path
        name: query
        type: string
        required: true
        description: query to execute
    responses:
      200:
          description: query response
    '''
    result = initializeResult()
    if query in QUERY:
        payload = QUERY[query]['query']
        result['rest']['payload'] = payload
        try:
            es_result = esearch.search(index=QUERY[query]['index'],
                                       body=payload)
        except Exception as ex:
            raise InvalidUsage(str(ex))
        result['result'] = es_result
    else:
        raise InvalidUsage("Query " + query + " was not found", 404)
    return generateResponse(result)


@app.route('/hitcount/<string:index>/<string:period>', methods=['GET'])
def hitcount(index, period):
    '''
    Return number of hits in the last specified time period
    Return the total number of ES hits over the last specified 
    time period for a specified index.
    ---
    tags:
      - General
    parameters:
      - in: path
        name: index
        type: string
        required: true
        description: index to query
      - in: path
        name: period
        type: string
        required: true
        description: time period (1s, 5m, 1h, 7d, etc.)
    responses:
      200:
          description: number of hits in the last time period
    '''
    result = initializeResult()
    payload = {"query": {"range": {"@timestamp": {"gte": "now-" + period}}}}
    result['rest']['payload'] = payload
    try:
        es_result = esearch.search(index=index, body=payload,
                                   filter_path=['hits.total'])
    except Exception as ex:
        raise InvalidUsage(str(ex))
    result['result'] = es_result['hits']['total']
    return generateResponse(result)


@app.route('/hitcount/<string:index>', methods=['GET'])
def hitcount_minute(index):
    '''
    Number of ES hits in the last minute
    Return the total number of ES hits over the last minute.
    ---
    tags:
      - General
    parameters:
      - in: path
        name: index
        type: string
        required: true
        description: index to query
    responses:
      200:
          description: number of hits in the last minute
    '''
    result = initializeResult()
    payload = {"query": {"range": {"@timestamp": {"gte": "now-1m"}}}}
    result['rest']['payload'] = payload
    try:
        es_result = esearch.search(index=index, body=payload,
                                   filter_path=['hits.total'])
    except Exception as ex:
        raise InvalidUsage(str(ex))
    result['result'] = es_result['hits']['total']
    return generateResponse(result)


@app.route('/hits/<string:index>', methods=['GET'])
def hits(index):
    '''
    Return ES hits
    Return the ES hits with user-specified filtering criteria. Filtering 
    criteria may be specified in the query, or in the body. If specified 
    in the body, it can be a JSON string or form data. Note that "start"
    and "end" are required, and must be epoch seconds.
    ---
    tags:
      - General
    parameters:
      - in: path
        name: index
        type: string
        required: true
        description: index to query
    responses:
      200:
          description: hits
    '''
    result = initializeResult()
    parm = get_parameters(result)
    missing = ''
    for p in ['start', 'end']:
        if p not in parm:
            missing = missing + p + ' '
    if missing:
        raise InvalidUsage('Missing arguments: ' + missing)
    must = []
    for p in parm:
        if p in ['start', 'end']:
            continue
        must.append({"term": {p: parm[p].lower()}})
    payload = {"size": 10000,
               "query": {"bool": {"filter": {"range": {"@timestamp": {"gte": parm['start'],
                                                  "lte": parm['end'],
                                                  "format": "epoch_second"}}}}}}
    if len(must):
        payload['query']['bool']['must'] = must
    result['rest']['payload'] = payload
    try:
        es_result = esearch.search(index=index, body=payload)
    except Exception as ex:
        raise InvalidUsage(str(ex))
    result['result'] = es_result
    return generateResponse(result)


# *****************************************************************************


if __name__ == '__main__':
    app.run(debug=True)
