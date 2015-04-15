from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from app import db
from models import Video, Record, Channel

sql_url = "mysql://root:@localhost/mmq"
db_engine = create_engine(sql_url)

table_sql = CreateTable(Video.__table__).compile(db_engine)
print str(table_sql)
table_sql = CreateTable(Channel.__table__).compile(db_engine)
print str(table_sql)
table_sql = CreateTable(Record.__table__).compile(db_engine)
print str(table_sql)
