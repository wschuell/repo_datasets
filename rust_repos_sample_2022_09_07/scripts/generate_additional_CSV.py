import os

import repodepo as rd
import repodepo.extras
from repodepo.getters import combined_getters

import datetime


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

csv_output_folder = os.path.join(output_folder,'examples','preprocessed')

time_window = 'month'
with_reponames = True
with_usernames = False

if not os.path.exists(csv_output_folder):
	os.makedirs(csv_output_folder)

#db.cursor.execute('SELECT COALESCE(MAX(created_at),CURRENT_TIMESTAMP) FROM packages;')
#end_date = db.cursor.fetchone()[0].replace(tzinfo=None)

end_date = datetime.datetime(2022,9,7)

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

