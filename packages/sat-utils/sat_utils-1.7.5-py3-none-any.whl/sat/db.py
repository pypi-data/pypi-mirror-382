from enum import Enum

import cx_Oracle
import oracledb
import pyodbc


class SatDBException(BaseException):
    pass


class ConnectionType(Enum):
    CX_ORACLE = 1
    PY_ORACLE = 2
    SQL = 3


def get_db_connection(conn_type: ConnectionType, **kwargs):
    """
    A function that returns a database connection.

    Parameters
    ----------
    conn_type: ConnectionType
        The database driver the connection uses.
    kwargs[conn_string]: A connection string.
    kwargs[conn_dict]: A dictionary of connection parameters.

    Returns
    -------
    A database connection object.

    Raises
    ------
    SatDBException
    """
    try:
        if conn_type == ConnectionType.SQL:
            return pyodbc.connect(kwargs.get("conn_string"))
        if conn_type == ConnectionType.CX_ORACLE:
            return cx_Oracle.connect(kwargs.get("conn_string"))
        if conn_type == ConnectionType.PY_ORACLE:
            return oracledb.connect(**kwargs.get("conn_dict"))
    except Exception as error:
        raise SatDBException(
            f"There was an {error.__class__.__name__} when connecting to the database: {error}"
        )
