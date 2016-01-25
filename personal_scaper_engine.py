'''Module for scraping Craigslist'''

from bs4 import BeautifulSoup
import urllib2
import re
import pickle
import MySQLdb
import json
from pandas import DataFrame, Series
from pandas.io import sql
import pandas as pd
import utilities
reload(utilities)
import utilities as ut
import datetime as dt
import sys
from sqlalchemy import create_engine
import pandasql
import numpy as np
import re
import psycopg2
from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://pawan:123@localhost/carsdb')
  




def connectn():
    df = DataFrame(columns=['year',
                                 'model',
                                 'price',
                                 'miles',
                                 'lat',
                                 'lon',
                                 'date',
                                 'area',
                                 'title',
                                 'body',
                                 'phone',
                                 'image_count',
                                 'url'])
    conn = psycopg2.connect(user="pawan", passwd="", dbname="carsdb")
    conn.cursor().execute('SET NAMES utf8;')
    conn.cursor().execute('SET CHARACTER SET utf8;')
    conn.cursor().execute('SET character_set_connection=utf8;')
    
    return conn



def drop_if_exists(engine, table_name):
    '''
    Deletes SQL table if it exists
    Args:
        conn - MySQLdb connection
        table_name (string)
    '''
    if pd.io.sql.table_exists(table_name, engine):
        pd.io.sql.uquery("DROP TABLE " + table_name, engine)


def prepare_table_w_textcols(df, table_name, engine, text_columns):
    '''
    Sets new MySQL table scheme to conform to pandas data_frame schema. For long
    columns of text, uses a text datatype instead of default varchar (63)
    Args:
        df (DataFrame)
        table_name (string)
        conn - MySQLdb connection
        text_columns - list of DataFrame columns that are text (list)
    '''
    cmd = pd.io.sql.get_schema(df, table_name, con=engine)
    for col in text_columns:
        cmd = re.sub(
            r"`" +
            col +
            "` VARCHAR \(63\)",
            r"`" +
            col +
            "` TEXT",
            cmd)
    pd.io.sql.execute(cmd, engine)


def create_table(engine,df):
    #sql.to_sql(df,'scraped', engine , if_exists='append', index=False)
    df.to_sql('scraped', engine , if_exists='append', index=False)
    



def main(df):
    #conn = connectn()

    if not engine:
        print "no Connection object found"
    drop_if_exists(engine, 'scraped')
    print "dropping table went fine"
    df['body'] = df['title']
    print "creating table went fine"
    prepare_table_w_textcols(df, 'scraped', engine, ['title','body'])
    create_table(engine,df)

    



def load_df(pickle_file):
    df = pd.read_pickle(pickle_file)
    return df

def print_df(df):
    q = """ select * from df """
    cars = pandasql.sqldf(q.lower(),locals())
    print cars

if __name__ == '__main__':
    pickle_file = sys.argv[1]
    df = load_df(pickle_file)
    print "the df is loaded"
    print_df(df)
    main(df)
        
    
































    

