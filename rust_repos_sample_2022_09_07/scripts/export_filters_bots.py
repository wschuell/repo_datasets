
import os
import oyaml as yaml

import repodepo as rd
import repodepo.extras
import repodepo.extras.exports






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

db = rd.repo_database.Database(**db_conninfo)

b_output_folder = os.path.join(output_folder,'scripts','data')
f_output_folder = os.path.join(b_output_folder,'filters')

if not os.path.exists(f_output_folder):
    os.makedirs(f_output_folder)

repodepo.extras.exports.export_filters(db=db,folder=f_output_folder)
repodepo.extras.exports.export_bots(db=db,folder=b_output_folder)
