from hashlib import md5

from flask import Flask, render_template, request, jsonify, make_response

from erd_viewer.loader.redis import RedisClient
from erd_viewer.graph import RelatedTables

app = Flask(__name__)

def get_decoded_list(l: list) -> list:
    return [x.decode('utf-8') for x in l]

def get_hash(*args: str) -> str:
    kwargs_string = ':'.join(list(args)).encode('utf-8')
    return md5(kwargs_string).hexdigest()

@app.route('/', methods=['GET', 'POST'])
def index():

    redis = RedisClient().get_client()
    schemas = sorted(get_decoded_list(redis.lrange('schemas:list', 0, -1)), key=str.casefold)
    tables = sorted(get_decoded_list(redis.hkeys(schemas[0])), key=str.casefold)
    return render_template('relatedtables.html', schemas=schemas, tables=tables)

@app.route('/get_tables', methods=['POST'])
def get_tables():

    redis = RedisClient().get_client()
    schema = request.form.get('schema')
    tables = sorted(get_decoded_list(redis.hkeys(schema)), key=str.casefold)
    return jsonify(tables)

@app.route('/render_relatedtables', methods=['POST'])
def render_related_tables():
    redis = RedisClient().get_client()

    schema = request.form.get('schema')
    table = request.form.get('table')
    depth = int(request.form.get('depth'))
    onlyrefs = bool(int(request.form.get('onlyrefs')))

    params_hash = get_hash(schema, table, str(depth), str(onlyrefs))
    svg = redis.hget('cached:svg', params_hash)

    if svg is None:
        svg = RelatedTables(schema, table, depth, onlyrefs).get_graph()
        redis.hset('cached:svg', params_hash, svg)

    response = make_response(svg)
    response.headers['Content-Encoding'] = 'gzip'
    response.headers["Content-Type"] = 'image/svg+xml'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4444, debug=True)