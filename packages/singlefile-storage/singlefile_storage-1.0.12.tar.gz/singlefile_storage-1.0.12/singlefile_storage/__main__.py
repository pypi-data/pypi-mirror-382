#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: qicongsheng
import argparse
import os
import sys

from singlefile_storage import help
from singlefile_storage import storage

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))


def main():
    parser = argparse.ArgumentParser(f"{help.get_name()} {help.get_version()} ({help.get_source_url()})")
    parser.add_argument('-data-path', '--data-path', default=os.getenv("DATA_PATH", "/data/singlefile"), type=str,
                        help='data storage path',
                        required=False)
    parser.add_argument('-port', '--port', default=os.getenv("PORT", 5083), type=int, help='http proxy port',
                        required=False)
    parser.add_argument('-users', '--users', default=os.getenv("USERS", None),
                        type=lambda s: dict(item.split(':') for item in s.split(',')),
                        help='user & passwd')
    parser.add_argument('-api-key', '--api-key', default=os.getenv("API_KEY"), type=str, help='api-key',
                        required=False)
    args = parser.parse_args()
    storage.users = args.users if args.users is not None else storage.users
    storage.DATA_PATH = args.data_path if args.data_path is not None else storage.DATA_PATH
    storage.API_KEY = args.api_key if args.api_key is not None else storage.API_KEY
    storage.start(port=args.port)


if __name__ == "__main__":
    main()
