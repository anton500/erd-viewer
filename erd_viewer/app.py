from flask import Flask, render_template, request, jsonify

from erd_viewer.loader.redis import RedisClient
from erd_viewer.dot import RelatedTables

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():

    redis = RedisClient().get_client()
    schemas = sorted(redis.keys('*'), key=str.casefold)
    tables = sorted(redis.hkeys(schemas[0]), key=str.casefold)
    return render_template('relatedtables.html', schemas=schemas, tables=tables)

@app.route("/get_tables", methods=['POST'])
def get_tables():

    redis = RedisClient().get_client()
    schema = request.form.get('schema')
    tables = sorted(redis.hkeys(schema), key=str.casefold)
    return jsonify(tables)

@app.route("/render_relatedtables", methods=['POST'])
def render_related_tables():

    schema = request.form.get('schema')
    table = request.form.get('table')
    depth = int(request.form.get('depth'))
    onlykeys = request.form.get('onlykeys')

    svg = RelatedTables(schema, table, depth, onlykeys).get_graph()

    return str(svg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4444, debug=True)