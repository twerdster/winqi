"""CLI: python3 -m updated.cli {codebook,decode,simulate}."""
import argparse
import json
from pathlib import Path
from .core import Codebook, StreamDecoder, generate_codebook, simulate


def main(argv=None):
    parser = argparse.ArgumentParser(description='Bounded cyclic binary beacon code generation and simulation.')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ['codebook', 'simulate']:
        p = sub.add_parser(name)
        p.add_argument('--bits', type=int, default=13)
        p.add_argument('--count', type=int, default=6)
        p.add_argument('--packing', choices=['nonconstant', 'source-script', 'include-constants'], default='nonconstant')
        p.add_argument('--out', type=Path)
        if name == 'simulate':
            p.add_argument('--duration', type=float, default=12)
            p.add_argument('--observation-hz', type=int, default=10)
            p.add_argument('--fps', type=int, default=30)
    p = sub.add_parser('decode')
    p.add_argument('--codebook', type=Path, required=True)
    p.add_argument('stream', help='Binary observation sequence; skip missing observations.')
    p.add_argument('--out', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == 'decode':
            book = Codebook.from_dict(json.loads(args.codebook.read_text()))
            decoder = StreamDecoder(book)
            value = {'schema': 'winqi-decode-v1', 'decisions': [decoder.push(c) for c in args.stream]}
        else:
            book = generate_codebook(args.bits, args.count, args.packing)
            value = book.to_dict() if args.command == 'codebook' else simulate(book, args.duration, args.observation_hz, args.fps)
        text = json.dumps(value, indent=2) + '\n'
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text)
        else:
            print(text, end='')
    except (ValueError, KeyError, OSError) as error:
        parser.error(str(error))


if __name__ == '__main__':
    main()
