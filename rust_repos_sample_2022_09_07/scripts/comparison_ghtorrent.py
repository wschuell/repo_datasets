import repodepo as rd
import repodepo.extras
from repodepo.extras import ghtorrent_stats
import psycopg2

######## PARAMETERS ########

import os

db_name = 'rust_repos_sample'
port = 54320

# Where to output the files
output_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Where intermediary data is stored when recollecting data for rebuilding the database
data_folder = output_folder+'_data_folder'

# Where cloned repositories are stored (when recollecting data for rebuilding the database)
clones_folder = os.path.join(os.path.dirname(output_folder),db_name.split('_repos')[0]+'_repos','cloned_repos')


### DB connection infos
# Main DB connection info; where the data is collected/reconstructed from a dump
db_conninfo = dict( host = 'localhost',
					port = port,
					db_user = 'postgres',
					db_type = 'postgres',
					db_name = db_name,
					clone_folder = clones_folder,
					data_folder = data_folder)

# PG destination DB connection info; where the data is exported before processing (anonymization + cleaning)
db_dest_pg_conninfo = dict( host = 'localhost',
					port = port,
					db_user = 'postgres',
					db_type = 'postgres',
					db_name = db_name+'_export',
					data_folder = data_folder)

# SQLite destination DB connection info; where the data is exported before processing (anonymization + cleaning)
db_dest_sqlite_conninfo = dict(
					db_type = 'sqlite',
					db_name = db_name+'_export',
					data_folder = data_folder)

# GHTorrent DB connection info (PostgreSQL)
db_ght_conninfo = dict( host = 'localhost',
					port = port,
					user = 'postgres',
					database = 'ghtorrent')

# crates.io DB connection info (PostgreSQL)
db_crates_conninfo = dict( host = 'localhost',
					port = port,
					user = 'postgres',
					database = 'crates_db')


######## PARAMETERS ########
filepath = os.path.join(output_folder,'statistics','ghtorrent_comparison.yml')

if not os.path.exists(filepath):
	db = rd.repo_database.Database(**db_conninfo)
	ght_conn = psycopg2.connect(**db_ght_conninfo)
	ght_cur = ght_conn.cursor()
	
	gs = ghtorrent_stats.GHTorrentGlobalStats(db=db,ght_cur=ght_cur,ght_conn=ght_conn)
	gs.print_result()
	
	gs.save(filepath=filepath)
