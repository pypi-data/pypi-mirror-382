from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from pathlib import Path

path = Path(__file__).parent / 'db.sqlite3'
uri = f'sqlite:///{path}'
engine = create_engine(uri)
session = Session(engine)
Base = automap_base()
Base.prepare(engine)

table_author = Base.classes.author
table_book = Base.classes.book
table_chapter = Base.classes.chapter
table_article = Base.classes.article

field = {table_name: [field for field in dir(table_object) if field.endswith('_id')] for table_name, table_object in locals().items() if table_name.startswith('table_')}

rank2table = {len(table_object): table_name for table_name, table_object in field.items()}

rank_sorted = sorted(rank2table.keys())

table2rank = {value: key for key, value in rank2table.items()}

name_map = {table_name[6:]: f'{table_name[6:]}_id' for table_name, table_object in locals().items() if table_name.startswith('table_')}

table_name_next = {rank2table[rank]: rank2table[rank + 1] if rank < 3 else None for rank in rank_sorted}
name2object = {table_name: table_object for table_name, table_object in locals().items() if table_name.startswith('table_')}