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
    conn = MySQLdb.connect(user="root", passwd="", db="carsdb")
    conn.cursor().execute('SET NAMES utf8;')
    conn.cursor().execute('SET CHARACTER SET utf8;')
    conn.cursor().execute('SET character_set_connection=utf8;')
    
    return conn



def drop_if_exists(conn, table_name):
    '''
    Deletes SQL table if it exists
    Args:
        conn - MySQLdb connection
        table_name (string)
    '''
    if pd.io.sql.table_exists(table_name, conn, flavor="mysql"):
        pd.io.sql.uquery("DROP TABLE " + table_name, conn)


def prepare_table_w_textcols(df, table_name, conn, text_columns):
    '''
    Sets new MySQL table scheme to conform to pandas data_frame schema. For long
    columns of text, uses a text datatype instead of default varchar (63)
    Args:
        df (DataFrame)
        table_name (string)
        conn - MySQLdb connection
        text_columns - list of DataFrame columns that are text (list)
    '''
    cmd = pd.io.sql.get_schema(df, table_name, 'mysql')
    for col in text_columns:
        cmd = re.sub(
            r"`" +
            col +
            "` VARCHAR \(63\)",
            r"`" +
            col +
            "` TEXT",
            cmd)
    pd.io.sql.execute(cmd, conn)


def create_table(conn,df):
    sql.to_sql(df,'scraped', conn, if_exists='append', flavor='mysql',index=False)
    



def main(df):
    conn = connectn()
    if not conn:
        print "no Connection object found"
    drop_if_exists(conn, 'scraped')
    print "dropping table went fine"
    df['body'] = df['title']
    #create_table(conn,df)
    prepare_table_w_textcols(df, 'scraped', conn, ['title','body'])
    create_table(conn,df)

    



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
        
    
































    

