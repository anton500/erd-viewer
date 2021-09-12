from flask import Flask, render_template
from erd_viewer.loader.redis import RedisClient

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():

    redis = RedisClient().r
    schemas = sorted(redis.keys('*'), key=str.casefold)
    tables = sorted(redis.hkeys('dlfe'), key=str.casefold)

    return render_template('graph.html', schemas=schemas, tables=tables)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4444, debug=True)