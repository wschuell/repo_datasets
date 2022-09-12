import os
import glob

split_str = '######## PARAMETERS ########'

param_str = '''

import os

db_name = 'rust_repos_sample'
port = 5432

# Where to output the files
output_folder = os.path.dirname(os.path.dirname(__file__))

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


'''


def set_params(filepath):
	with open(filepath,'r') as f:
		file_content = f.read()

	splitted_file_content = file_content.split(split_str)

	if len(splitted_file_content) >= 3 and splitted_file_content[1] != param_str:
		print('Updating params in file {}'.format(filepath))
		splitted_file_content[1] = param_str
		new_file_content = split_str.join(splitted_file_content)
		with open(filepath,'w') as f:
			f.write(new_file_content)


if __name__ == '__main__':
	file_list = glob.glob(os.path.join(os.path.dirname(__file__),'*.py'))
	for filepath in file_list:
		set_params(filepath=filepath)
