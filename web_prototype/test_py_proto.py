from datetime import datetime
import pytest
import sqlite3
from uuid import uuid4
import os
from unittest.mock import MagicMock
import sys
from py_proto import ExcelButBetter, num_to_colname, colname_to_num, indexed_to_array, array_to_indexed
from hypothesis import strategies as st, given, settings, Verbosity, Phase

positive_ints = st.integers(min_value=0)
ints = lambda low, high: st.integers(min_value=low, max_value=high)

@given(positive_ints)
def test_colname_to_num_roundtrip(j):
    assert colname_to_num(num_to_colname(j)) == j

@given(st.lists(st.tuples(ints(0, 1_000_000), ints(0, 2000), st.text(min_size=1)), unique_by=lambda t: (t[0], t[1])))
@settings(deadline=None)
def test_indexed_to_array_roundtrip(a):
    a = sorted(a)
    assert array_to_indexed(indexed_to_array(a)) == a

def test_indexed_to_array():
    # Base case
    assert indexed_to_array([(0, 0, 'foo'), (0, 1, 'bar'), (1, 0, 'baz'), (1, 1, 'boo')]) == [['foo', 'bar'], ['baz', 'boo']]

    # Empty rows and cells
    assert indexed_to_array([(1, 3, 'foo')]) == [[], ['', '', '', 'foo']]

@pytest.fixture
def tmp_db():
  tmp_db_name = f'{uuid4()}.sqlite'
  conn = sqlite3.connect(tmp_db_name)
  c = conn.cursor()
  conn.execute(f'create table test (row integer, column integer, value text, valid_from timestamp, valid_to timestamp)')
  now = datetime.now()
  to_insert = [(0, 0, 'foo', now, datetime.max), (0, 1, 'bar', now, datetime.max),
               (1, 0, 'baz', now, datetime.max), (1, 1, 'boo', now, datetime.max)]
  conn.executemany('insert into test values (?, ?, ?, ?, ?)', to_insert)
  conn.commit()
  conn.close()
  yield tmp_db_name
  os.unlink(tmp_db_name)

def test_modify(tmp_db):
  ebb = ExcelButBetter(tmp_db)
  
  # Inplace
  ebb.update_cell(0, 0, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar'], ['baz', 'boo']]
  # Idempotent
  ebb.update_cell(0, 0, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar'], ['baz', 'boo']]

  # New column
  ebb.update_cell(0, 2, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo']]
  # Idempotent
  ebb.update_cell(0, 2, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo']]

  # New row
  ebb.update_cell(2, 0, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv']]
  # Idempotent
  ebb.update_cell(2, 0, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv']]

  # New row and column
  ebb.update_cell(3, 3, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], ['', '', '', 'vvvvv']]
  # Idempotent
  ebb.update_cell(3, 3, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], ['', '', '', 'vvvvv']]

  # New column with gaps
  ebb.update_cell(0, 5, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv', '', '', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], ['', '', '', 'vvvvv']]
  # Idempotent
  ebb.update_cell(0, 5, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv', '', '', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], ['', '', '', 'vvvvv']]

  # New row with gaps
  ebb.update_cell(5, 0, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv', '', '', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], ['', '', '', 'vvvvv'], [], ['vvvvv']]
  # Idempotent
  ebb.update_cell(5, 0, 'vvvvv')
  assert ebb.rows == [['vvvvv', 'bar', 'vvvvv', '', '', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], ['', '', '', 'vvvvv'], [], ['vvvvv']]

def test_commit(tmp_db):
  # Scenario's: insert new columns, insert new rows, update stuff
  ebb = ExcelButBetter(tmp_db)

  def get_table(tmp_db):
    conn = sqlite3.connect(tmp_db)
    now = datetime.now()
    result = conn.execute(f'select row, column, value from {ebb.safe_table_name} where ? between valid_from and valid_to', (now,)).fetchall()
    conn.close()
    return indexed_to_array(result)

  # Update
  ebb.update_cell(0, 0, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar'], ['baz', 'boo']]
  # Idempotent
  ebb.update_cell(0, 0, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar'], ['baz', 'boo']]

  # Insert rows
  ebb.update_cell(2, 0, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar'], ['baz', 'boo'], ['vvvvv']]
  # Idempotent
  ebb.update_cell(2, 0, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar'], ['baz', 'boo'], ['vvvvv']]

  # Insert columns
  ebb.update_cell(0, 2, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv']]
  # Idempotent
  ebb.update_cell(0, 2, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv']]

  # Insert rows and columns wtih skip
  ebb.update_cell(4, 4, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], [], ['', '', '', '', 'vvvvv']]
  # Idempotent
  ebb.update_cell(4, 4, 'vvvvv')
  ebb.commit()
  assert get_table(tmp_db) == [['vvvvv', 'bar', 'vvvvv'], ['baz', 'boo'], ['vvvvv'], [], ['', '', '', '', 'vvvvv']]
