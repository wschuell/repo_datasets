import os

import repodepo as rd
import repodepo.extras
from repodepo.getters import combined_getters




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
					db_name = 'rust_repos_sample',
					data_folder = data_folder)

# PG destination DB connection info; where the data is exported before processing (anonymization + cleaning)
db_dest_pg_conninfo = dict( host = 'localhost',
					port = 5432,
					db_user = 'postgres',
					db_type = 'postgres',
					db_name = 'rust_repos_sample_export',
					data_folder = data_folder)

# SQLite destination DB connection info; where the data is exported before processing (anonymization + cleaning)
db_dest_sqlite_conninfo = dict(
					db_type = 'sqlite',
					db_name = 'rust_repos_sample_export',
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

csv_output_folder = os.path.join(output_folder,'examples','preprocessed')

time_window = 'month'
with_reponames = True
with_usernames = False

if not os.path.exists(csv_output_folder):
	os.makedirs(csv_output_folder)

db.cursor.execute('SELECT COALESCE(MAX(created_at),CURRENT_TIMESTAMP) FROM packages;')
end_date = db.cursor.fetchone()[0].replace(tzinfo=None)

getter_params = dict(db=db,time_window=time_window,with_reponame=with_reponames,with_userlogin=with_usernames,end_date=end_date)

getters = [
	('usage',combined_getters.UsageGetter(**getter_params),),
	('dependencies',combined_getters.DepsGetter(**getter_params),),
	('contributions',combined_getters.ContributionsGetter(**getter_params),),
	]

for n,g in getters:
	if os.path.exists(os.path.join(csv_output_folder,'{}.csv'.format(n))):
		db.logger.info('Results of getter {} already dumped, skipping'.format(n))
	else:
		db.logger.info('Getting results of getter {}'.format(n))
		df = g.get_result()
		db.logger.info('Writing results of getter {}'.format(n))
		df.to_csv(os.path.join(csv_output_folder,'{}.csv'.format(n)),sep=',',header=True)
		del df
		db.logger.info('Over with getter {}'.format(n))

