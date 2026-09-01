#!/usr/bin/env python3
"""Copy an AI-rendered image without overwriting existing files; no image editing."""
import argparse
from datetime import datetime
from pathlib import Path


def save_output(source, workspace, ticket_type):
    if ticket_type not in ('airplane', 'railway'):
        raise ValueError('ticket_type must be airplane or railway')
    source = Path(source).resolve(strict=True)
    data = source.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        extension = '.png'
    elif data.startswith(b'\xff\xd8\xff'):
        extension = '.jpg'
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        extension = '.webp'
    else:
        raise ValueError('Expected a PNG, JPEG or WebP image; source left unchanged')
    destination = Path(workspace).resolve() / 'output' / 'travel-ticket'
    destination.mkdir(parents=True, exist_ok=True)
    stem = 'ticket-{}-{}'.format(ticket_type, datetime.now().strftime('%Y%m%d-%H%M%S'))
    version = 1
    while True:
        suffix = '' if version == 1 else '-v{}'.format(version)
        target = destination / (stem + suffix + extension)
        try:
            stream = target.open('xb')
        except FileExistsError:
            version += 1
            continue
        try:
            with stream:
                stream.write(data)
        except BaseException:
            # Only remove the incomplete file exclusively created by this call.
            target.unlink(missing_ok=True)
            raise
        return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--workspace', type=Path, default=Path.cwd())
    parser.add_argument('--type', choices=('airplane', 'railway'), required=True)
    args = parser.parse_args()
    try:
        print(save_output(args.source, args.workspace, args.type))
    except (OSError, ValueError) as error:
        parser.exit(1, 'Cannot save ticket: {}\n'.format(error))


if __name__ == '__main__':
    main()
