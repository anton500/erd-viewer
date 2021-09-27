from hashlib import md5

from flask import Flask, render_template, request, jsonify, make_response, Response

from erd_viewer.loader.redis import RedisClient
from erd_viewer.graph import RelatedTables, FindRoute
from erd_viewer.database import SchemaTable

app = Flask(__name__)

nav = [
    {'title': 'Find a route', 'url': '/findroute'},
    {'title': 'Related tables', 'url': '/relatedtables'},
    {'title': 'Schema', 'url': '/schema'},
    {'title': 'Database', 'url': '/database'}
]

def get_decoded_list(l: list) -> list:
    return [x.decode('utf-8') for x in l]

def get_hash(*args: str) -> str:
    args_string = ':'.join(list(args)).encode('utf-8')
    return md5(args_string).hexdigest()

def response_svg(svg: bytes) -> Response:
    response = make_response(svg)
    response.headers['Content-Encoding'] = 'gzip'
    response.headers["Content-Type"] = 'image/svg+xml'
    return response

@app.route('/', methods=['GET'])
@app.route('/findroute', methods=['GET'])
def findroute():
    redis = RedisClient().get_client()
    schemas = sorted(get_decoded_list(redis.lrange('schemas:list', 0, -1)), key=str.casefold)
    tables = sorted(get_decoded_list(redis.hkeys(schemas[0])), key=str.casefold)
    return render_template('findroute.html', schemas=schemas, tables=tables, nav=nav, url='/findroute')

@app.route('/relatedtables', methods=['GET'])
def relatedtables():
    redis = RedisClient().get_client()
    schemas = sorted(get_decoded_list(redis.lrange('schemas:list', 0, -1)), key=str.casefold)
    tables = sorted(get_decoded_list(redis.hkeys(schemas[0])), key=str.casefold)

    return render_template('relatedtables.html', schemas=schemas, tables=tables, nav=nav, url='/relatedtables')

@app.route('/schema', methods=['GET'])
def schema():
    redis = RedisClient().get_client()
    schemas = sorted(get_decoded_list(redis.lrange('schemas:list', 0, -1)), key=str.casefold)

    return render_template('schema.html', schemas=schemas, nav=nav, url='/schema')

@app.route('/database', methods=['GET'])
def database():
    redis = RedisClient().get_client()
    schemas = sorted(get_decoded_list(redis.lrange('schemas:list', 0, -1)), key=str.casefold)

    return render_template('database.html', schemas=schemas, nav=nav, url='/database')

@app.route('/get_tables', methods=['POST'])
def get_tables():

    redis = RedisClient().get_client()
    schema = request.form.get('schema')
    tables = sorted(get_decoded_list(redis.hkeys(schema)), key=str.casefold)
    return jsonify(tables)

@app.route('/render_findroute', methods=['POST'])
def render_findroute():
    redis = RedisClient().get_client()

    start_schema = request.form.get('start-schemas')
    start_table = request.form.get('start-tables')
    dest_schema = request.form.get('dest-schemas')
    dest_table = request.form.get('dest-tables')
    exclude = request.form.get('exclude')
    tables_to_exclude = [SchemaTable(exclude.split('.')[0], exclude.split('.')[1])] if exclude else []

    onlyrefs = bool(int(request.form.get('onlyrefs')))
    shortest = bool(int(request.form.get('shortest')))

    args_for_hash = (
        'findroute',
        start_schema,
        start_table,
        dest_schema,
        dest_table,
        exclude,
        str(onlyrefs),
        str(shortest),
    )

    params_hash = get_hash(*args_for_hash)
    svg = redis.hget('cached:svg', params_hash)

    if svg is None:
        svg = FindRoute(
            SchemaTable(start_schema, start_table),
            SchemaTable(dest_schema, dest_table),
            tables_to_exclude,
            onlyrefs,
            shortest,
        ).get_graph()
        redis.hset('cached:svg', params_hash, svg)

    return response_svg(svg)

@app.route('/render_relatedtables', methods=['POST'])
def render_related_tables():
    redis = RedisClient().get_client()

    schema = request.form.get('schemas')
    table = request.form.get('tables')
    exclude = request.form.get('exclude')
    tables_to_exclude = [SchemaTable(exclude.split('.')[0], exclude.split('.')[1])] if exclude else []
    depth = int(request.form.get('depth'))
    onlyrefs = bool(int(request.form.get('onlyrefs')))

    args_for_hash = (
        'relatedtables',
        schema,
        table,
        exclude,
        str(onlyrefs),
    )

    params_hash = get_hash(*args_for_hash)
    svg = redis.hget('cached:svg', params_hash)

    if svg is None:
        svg = RelatedTables(
            SchemaTable(schema, table),
            depth,
            tables_to_exclude,
            onlyrefs
        ).get_graph()
        redis.hset('cached:svg', params_hash, svg)

    return response_svg(svg)