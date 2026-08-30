#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize the SQLite database (safe to re-run)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import db


def main():
    db.init_db()
    print(f"DB ready: {os.path.abspath(db._db_path)}")
    print(f"articles: {db.article_count()}")


if __name__ == '__main__':
    main()
