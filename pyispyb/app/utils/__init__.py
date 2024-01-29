"""Project: py-ispyb.

https://github.com/ispyb/py-ispyb

This file is part of py-ispyb software.

py-ispyb is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

py-ispyb is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with py-ispyb. If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import datetime
from decimal import Decimal
import os
import time
import logging
from sqlalchemy import text
from functools import wraps
from pyispyb.config import settings
from sqlalchemy.orm import class_mapper
from sqlalchemy import inspect

logger = logging.getLogger("ispyb")


def get_sql_query(name, append=""):
    """Get sql query string from matching file.

    Args:
        name (str): name of the query
        append (str, optional): text to append at the end of the query. Defaults to "".

    Returns:
        str: query string
    """
    path = os.path.join(settings.queries_dir, name + ".sql")
    file = open(path)
    query_string = file.read() + append
    query = text(query_string)
    return query


def queryresult_to_dict(result):
    """Convert a sql query result to a python dictinary.

    Args:
        result : sql alchemy query result

    Returns:
        dict: converted result
    """
    res = []

    for row in result:
        row_dict = {}
        for field in row._mapping.items():
            field_name = field[0]
            field_value = field[1]
            if isinstance(field_value, datetime):
                field_value = field_value.isoformat()
            if isinstance(field_value, Decimal):
                field_value = float(field_value)
            row_dict[field_name] = field_value
        res.append(row_dict)

    return res


def timed(fn):
    """
    Decorator to log the time that a class function takes to execute
    """

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        result = fn(self, *args, **kwargs)
        took = round(time.time() - start, 3)
        logger.debug(f"Class {self.__class__} - Function {fn.__name__}  took {took}")

        return result

    return wrapper


def model_from_json(model, data):
    mapper = class_mapper(model)
    keys = mapper.attrs.keys()
    relationships = inspect(mapper).relationships
    args = {k: v for k, v in data.items() if k in keys and k not in relationships}
    return model(**args)
