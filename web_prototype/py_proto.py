import sqlite3
from io import BytesIO
from datetime import datetime
from pathlib import Path

NROWS = 100
NCOLS = 100

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
def num_to_colname(j):
  if j < len(alphabet): return alphabet[j]
  prefix = []  # Decimal expansion of j base len(alphabet), least significant digit first
  while j >= len(alphabet):
    j, idx = divmod(j, len(alphabet))
    prefix.append(idx)
  prefix.append(j)

  return alphabet[prefix[-1]-1] + ''.join(alphabet[i] for i in reversed(prefix[:-1]))

def colname_to_num(col):
  if len(col) == 1: return alphabet.index(col)
  indices = [alphabet.index(col[0]) + 1]
  for c in col[1:]:
      indices.append(alphabet.index(c))

  return sum(k*26**i for i, k in enumerate(reversed(indices)))

def indexed_to_array(rows): 
    '''Turns a list of rows of the form [(row, col, value)] into an array like [[value, value]]'''
    rows = sorted(rows)
    result = []
    this_row, previous_row_number = [], 0
    for row_number, col_number, value in rows:
        if row_number != previous_row_number:
            result.extend([this_row] + [[] for _ in range(previous_row_number+1, row_number)])
            this_row, previous_row_number = [], row_number
        this_row.extend([''] * (col_number - len(this_row)) + [value])
    result.append(this_row)
    return result

def array_to_indexed(rows):
    '''Turns an array like [[value, value]] into a list of rows of the form [(row, col, value)]'''
    return [(i, j, value) for i, row in enumerate(rows) for j, value in enumerate(row) if value]

class ExcelButBetter:
  def __init__(self, fname=':memory:'):
    self.safe_table_name = 'test'  # Todo(Rik): don't forget to escape!
    is_new_file = not Path(fname).exists()  # Connecting will create a file
    self.conn = sqlite3.connect(fname, detect_types=sqlite3.PARSE_DECLTYPES)
    if is_new_file:
      self.conn.execute(f'create table {self.safe_table_name} (row integer, column integer, value text, valid_from timestamp, valid_to timestamp, primary key (row asc, column asc))')
      self.conn.commit()

    self.refresh()

  @classmethod
  def from_file(cls, b):
    from js import file
    b = file.to_py().tobytes()
    fname = 'tmp.sqlite'
    with open(fname, 'wb+') as handle:
      handle.write(b)
    return cls(fname)

  @property
  def rows(self):
    return indexed_to_array(self._data)

  def refresh(self):
    self.c = self.conn.cursor()
    now = datetime.now()
    self._data = self.c.execute(f'select row, column, value from {self.safe_table_name} where ? between valid_from and valid_to order by row, column', (now,)).fetchall()
    self.nrow_in_table = max((row_number for row_number, col_number, value in self._data), default=0)
    self.ncol_in_table = max((col_number for row_number, col_number, value in self._data), default=0)
    return self.rows

  def update_cell(self, i, j, value):
    value = value.strip()
    if not value: return
    try:
        idx = [(i, j) == (i_, j_) for (i_, j_, v) in self._data].index(True)
        self._data[idx] = (i, j, value)
    except ValueError:  # Element not in list
        self._data.append((i, j, value))
  
  def commit(self):
    now = datetime.now()
    original = self.c.execute(f'select row, column, value from {self.safe_table_name} where ? between valid_from and valid_to', (now,)).fetchall()
    og_dict = {(i, j): v for i, j, v in original if v}
    new_dict = {(i, j): v for i, j, v in self._data if v}

    to_delete = [idx for idx in og_dict.keys() - new_dict.keys()]
    to_insert = [(*idx, new_dict[idx]) for idx in new_dict.keys() - og_dict.keys() if new_dict[idx]]
    to_update = [(*idx, new_dict[idx]) for idx in new_dict.keys() & og_dict.keys() if new_dict[idx] != og_dict[idx]]

    now = datetime.now()
    insert_data = [(i, j, v, now, datetime.max) for i, j, v in to_insert]
    self.c.executemany(f'insert into {self.safe_table_name} values (?, ?, ?, ?, ?)', insert_data)

    delete_data = [(now, i, j) for i, j in to_delete]
    self.c.executemany(f'update {self.safe_table_name} set valid_to=? where row=? and column=?', delete_data)

    update_data = [(now, i, j) for i, j, v in to_update]
    self.c.executemany(f'update {self.safe_table_name} set valid_to=? where row=? and column=?', update_data)
    update_data = [(i, j, v, now, datetime.max) for i, j, v in to_update]
    self.c.executemany(f'insert into {self.safe_table_name} values (?, ?, ?, ?, ?)', update_data)
    
    self.conn.commit()
    self.refresh()
  
  def table_to_html(self):
    result = [f'<table id="{self.safe_table_name}">']
    result.append('<tr><th class="rownum"></th>')
    result.extend([f'<th>{num_to_colname(j)}</th>' for j in range(NCOLS)])
    result.append('</tr>')
    for i in range(NROWS):
      result.append(f'<tr><td class="rownum">{i+1}</td>')
      result.extend([f'<td contenteditable>{self.rows[i][j] if i < len(self.rows) and j < len(self.rows[i]) else ""}</td>' for j in range(NCOLS)])
      result.append('</tr>')
    result.append('</table>')
    return ''.join(result)

try:
  from js import file
  b = file.to_py().tobytes()
  fname = 'tmp.sqlite'
  with open(fname, 'wb+') as handle:
    handle.write(b)
  ebb = ExcelButBetter(fname)
  update_cell = ebb.update_cell
  commit = ebb.commit
  table_to_html = ebb.table_to_html
except ImportError:
  print('No js module found, not running main scripts.')
    

