import pandas as pd
import numpy as np
import re

from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg2://pawan:123@localhost/carsdb')


def get_xval_indcs(n, training_frac):
    '''
    Args:
        n - number of items (int)
        training_fra - fraction of items to be used for training (float)
    Returns:
        array of training idcs and array of testing_idcs (np array)
    '''
    training_n = round(training_frac * n)
    data_idcs = np.random.permutation(range(0, n - 1))
    training_idcs = data_idcs[:training_n]
    testing_idcs = data_idcs[training_n:]

    return training_idcs, testing_idcs


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
    print "Schema Copied"
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
