"""Module for extracting data from RDS."""


from logging import getLogger
from os import environ as ENV

from dotenv import load_dotenv
from pandas import DataFrame
from pyodbc import connect, Connection
