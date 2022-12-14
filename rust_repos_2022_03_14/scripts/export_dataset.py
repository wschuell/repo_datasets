
import os
import oyaml as yaml

import repodepo as rd
import repodepo.extras
import repodepo.extras.exports



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


tables_filter_file = os.path.join(os.path.dirname(__file__),'data','tables_filter.yml')
with open(tables_filter_file,'r') as f:
    inclusion_list = yaml.safe_load(f.read())

export_output_folder = os.path.join(output_folder,'dumps')

if not os.path.exists(export_output_folder):
    os.makedirs(export_output_folder)

db_orig = rd.repo_database.Database(**db_conninfo)
db_dest_pg = rd.repo_database.Database(**db_dest_pg_conninfo)
db_dest_sqlite = rd.repo_database.Database(db_folder=os.path.join(export_output_folder,'sqlite'),**db_dest_sqlite_conninfo)

# Export to a postgres DB, where it will be anonymized and cleaned
repodepo.extras.exports.export(orig_db=db_orig,dest_db=db_dest_pg,ignore_error=True)
repodepo.extras.anonymize(db=db_dest_pg,keep_email_suffixes=False,ignore_error=True)

# Exporting to a SQLite DB
repodepo.extras.exports.export(orig_db=db_dest_pg,dest_db=db_dest_sqlite,ignore_error=True)

#Cleaning both DBs to keep only relevant tables and attributes
repodepo.extras.exports.clean(db=db_dest_sqlite,inclusion_list=inclusion_list,vacuum_sqlite=False)
repodepo.extras.exports.clean(db=db_dest_pg,inclusion_list=inclusion_list)

# Dumping to schema.sql, import.sql + table CSV files
repodepo.extras.exports.dump_pg_csv(db=db_dest_pg,output_folder=os.path.join(export_output_folder,'postgresql'))
