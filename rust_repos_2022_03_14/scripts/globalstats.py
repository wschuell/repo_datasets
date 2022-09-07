import repodepo as rd
import repodepo.extras


######## PARAMETERS ########

import os

# Where to output the files
output_folder = os.path.dirname(os.path.dirname(__file__))

# Where intermediary data is stored when recollecting data for rebuilding the database
data_folder = os.path.join(output_folder,'data_folder')

# Where cloned repositories are stored (when recollecting data for rebuilding the database)
clones_folder = data_folder


### DB connection infos
# Main DB connection info; where the data is collected/reconstructed from a dump
db_conninfo = dict( host = 'localhost',
					port = 5432,
					db_user = 'postgres',
					db_type = 'postgres',
					db_name = 'rust_repos',
					data_folder = data_folder)

# PG destination DB connection info; where the data is exported before processing (anonymization + cleaning)
db_dest_pg_conninfo = dict( host = 'localhost',
					port = 5432,
					db_user = 'postgres',
					db_type = 'postgres',
					db_name = 'rust_repos_export',
					data_folder = data_folder)

# SQLite destination DB connection info; where the data is exported before processing (anonymization + cleaning)
db_dest_sqlite_conninfo = dict(
					db_type = 'sqlite',
					db_name = 'rust_repos_export',
					data_folder = data_folder)

# GHTorrent DB connection info (PostgreSQL)
db_ght_conninfo = dict( host = 'localhost',
					port = 5432,
					user = 'postgres',
					database = 'ghtorrent')

# crates.io DB connection info (PostgreSQL)
db_crates_conninfo = dict( host = 'localhost',
					port = 5432,
					user = 'postgres',
					database = 'crates_db')


######## PARAMETERS ########

db = rd.repo_database.Database(**db_conninfo)
gs = repodepo.extras.GlobalStats(db=db)
gs.print_result()
gs.save(filepath=os.path.join(output_folder,'statistics','global_stats.yml'))
