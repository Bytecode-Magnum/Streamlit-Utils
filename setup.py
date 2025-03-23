import streamlit as st
import os
from io import BytesIO
from datetime import datetime
import polars as pl
import pandas as pd
import time
import requests
import io
from typing import List, Optional
import csv
import zipfile
import openpyxl
import psycopg2 as pg
from dotenv import load_dotenv
import sys
import numpy as np
import streamlit.web.cli as stcli
from src.components.conversionRate import currencyConversion
from src.components.appendFiles import appendFiles
from src.components.exportFile import exportFile
from src.components.compareData import compareData
from src.components.importFile import importFile
from src.components.fileConvertor import fileConvertor


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("app.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())