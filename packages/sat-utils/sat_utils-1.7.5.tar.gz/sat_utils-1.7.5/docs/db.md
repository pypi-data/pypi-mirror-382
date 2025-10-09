# Database Module

## Overview

The dabase module aims to standardize how we connect to our data environments

It currently supports two database engines, Oracle and SQL server.
Support for SQL server is provided by pyodbc while support for Oracle is provided by cx_Oracle.

The current supported connection types are ConnectionType.SQL and ConnectionType.ORACLE.

**install**

`pip install --extra-index https://pypi.ehps.ncsu.edu sat-utils`

##Usage

**getting connected with a connection string**

```
from sat.db import ConnectionType as ctype, get_db_connection
from os import getenv

connection_string = 'user/password@localhost/orcl'
connection = get_db_connection(connection_string, ctype.ORACLE)
```

**getting connected with an environment variable**

```
from sat.db import ConnectionType as ctype, get_named_db_connection

connection = get_db_connection('ENV_PROD_CONNECTION', ctype.ORACLE)
```
