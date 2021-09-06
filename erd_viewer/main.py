import argparse
import uuid
from pathlib import Path

from erd_viewer.dot import Dot

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create DOT file for Graphviz render from db schema.')
    parser.add_argument('-f', '--file', dest='file', help='json file containing db schema', required=True, type=Path)
    parser.add_argument('-n', '--name', dest='name', help='graph name', type=str)
    #parser.add_argument('-o', '--output', dest='output', help='output dot file', required=True, type=Path)
    #parser.add_argument('-r', '--render', dest='render', help='output rendered file', type=Path)
    parser.add_argument('-s', '--schema', dest='schema', help='process only selected schema')
    parser.add_argument('-t', '--table', dest='table', help='process only selected tables')
    parser.add_argument('--no-render', dest='norender', help='only save, don\'t render')

    return parser.parse_args()

def main(args) -> str:
    database = None
    dot = Dot(database)
    digraph = dot.get_digraph(
        name=args.name if args.name else str(uuid.uuid4()),
        engine='neato',
        format='svg',
        graph_attr={'splines': 'spline', 'overlap': 'prism'}, 
        node_attr={'shape': 'plaintext'}
    )

    if args.norender is None:
        return digraph.render(directory=Path('erd-viewer/static/graphs'), cleanup=True)
    return
     
if __name__ == '__main__':
    main(parse_args())