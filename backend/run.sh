#!/bin/bash
python -m pip install -r requirements.txt`
python src/crawler.py`
python src/indexer.py`
python src/app.py`