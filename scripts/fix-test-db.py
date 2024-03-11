#!/usr/bin/env python


# The content of the database in the Docker image is inconsistent
# and needs to be fixed before using it.


import os
import sys

import sqlalchemy


DEFAULT_URI = "mysql+mysqlconnector://test:test@127.0.0.1/test"


# The value of `AUTO_INCREMENT` for the `BeamLineSetup` table is incorrect.
# Its value should be `1761429`.
SQL = "ALTER TABLE BeamLineSetup AUTO_INCREMENT = 1761429"


def main():
    uri = os.environ.get("SQLALCHEMY_DATABASE_URI", DEFAULT_URI)
    engine = sqlalchemy.create_engine(uri, echo=True, future=True)
    with engine.connect() as db_connection:
        db_connection.execute(sqlalchemy.text(SQL))
        db_connection.commit()


if __name__ == "__main__":
    sys.exit(main())
