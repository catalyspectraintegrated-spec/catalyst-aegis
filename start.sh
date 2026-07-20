#!/bin/bash
python init_db.py
streamlit run Home.py --server.headless true --server.port $PORT --server.address 0.0.0.0
