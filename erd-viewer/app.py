from pathlib import Path

from flask import Flask, render_template, Markup

app = Flask(
    __name__, 
    static_url_path='', 
    static_folder='static',
    template_folder='templates'
)

@app.route("/")
def hello_world():
    svg = open(Path('erd-viewer/static/graph.gv.svg')).read()
    return render_template('graph.html', svg=Markup(svg))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='4444', debug=True)