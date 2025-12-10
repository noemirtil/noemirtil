import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    # Within an application context, get_db should return the same connection each time it’s called.
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    # After the context, the connection should be closed.
    assert 'closed' in str(e.value)

def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    # This test uses Pytest’s monkeypatch fixture to replace the init_db function with one that records that it’s been called.
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)
    # The init-db command should call the init_db function and output a message. The runner fixture is used to call the init-db command by name.
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called