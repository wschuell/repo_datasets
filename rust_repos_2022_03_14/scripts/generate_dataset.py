
import repo_tools as rp
from repodepo.fillers import generic,github_rest,commit_info,crates,julia,github_gql,gitlab_gql,meta_fillers,deps_filters_fillers
import os
import psycopg2
import time



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

# package_limit = 100 # Set a package limit to build a sample dataset, from the N first packages by id. If set to None, no limit.
package_limit = None # Set a package limit to build a sample dataset, from the N first packages by id. If set to None, no limit.


workers = 6 # Number of parallel threads for querying the github APIs

print('Make sure you have a github API key (with permission read:user for GraphQL) in $HOME/.repo_tools/github_api_keys.txt. Continuing in 3s.')
print('Make sure you have a gitlab API key in $HOME/.repo_tools/gitlab_api_keys.txt. Continuing in 3s.')
time.sleep(3)


db = rp.repo_database.Database(**db_conninfo)

db.init_db()
db.add_filler(generic.SourcesFiller(source=['GitHub','Gitlab'],source_urlroot=['github.com','gitlab.com']))
db.add_filler(crates.CratesFiller(package_limit=package_limit,**db_crates_conninfo)) # Filling in informations from a crates database: packages, urls, versions, dependencies, downloads

db.add_filler(generic.RepositoriesFiller()) # Parses the URLs of the packages to attribute them to the available sources (github.com and gitlab.com)
db.add_filler(github_gql.ForksGQLFiller(workers=workers))
db.add_filler(generic.ClonesFiller(data_folder=clones_folder)) # Clones after forks to have up-to-date repo URLS (detect redirects)
db.add_filler(commit_info.CommitsFiller(data_folder=clones_folder)) # Commits after forks because fork info needed for repo commit ownership ran at the end.
db.add_filler(generic.RepoCommitOwnershipFiller()) # associating repositories as owners of commits (for those who could not be disambiguated using forks) based on creation date of associated package
db.add_filler(generic.GithubNoreplyEmailMerger()) # Resolves commit authors with email @users.noreply.github.com
db.add_filler(github_gql.LoginsGQLFiller(workers=workers)) # Disambiguating emails by associating them to their GH logins, using the most recent commit.
db.add_filler(github_gql.RandomCommitLoginsGQLFiller(workers=workers)) # Disambiguating emails by associating them to their GH logins, using a random commit.
db.add_filler(gitlab_gql.LoginsFiller(workers=workers)) # Disambiguating emails by associating them to their GL logins, using the most recent commit.
db.add_filler(gitlab_gql.RandomCommitLoginsFiller(workers=workers)) # Disambiguating emails by associating them to their GL logins, using a random commit.
db.add_filler(generic.SimilarIdentitiesMerger(identity_type1='github_login',identity_type2='gitlab_login'))
db.add_filler(github_gql.StarsGQLFiller(workers=workers))
db.add_filler(github_gql.FollowersGQLFiller(workers=workers))
db.add_filler(github_gql.SponsorsUserFiller(workers=workers))
db.add_filler(generic.RepoCommitOwnershipFiller())
db.add_filler(meta_fillers.MetaBotFiller()) # wrapping several techniques to flag bots and invalid identities
db.add_filler(github_gql.RepoCreatedAtGQLFiller(workers=workers))
db.add_filler(gitlab_gql.RepoCreatedAtFiller(workers=workers))
db.add_filler(github_gql.UserCreatedAtGQLFiller(workers=workers))
db.add_filler(github_gql.RepoLanguagesGQLFiller(workers=workers)) # Filling in repository language shares (approximation made directly by GitHub)
db.add_filler(github_gql.UserLanguagesGQLFiller(workers=workers)) # Compiling an approximation of user contributions in each language over a time period (default one year up to query time)
db.add_filler(deps_filters_fillers.AutoRepoEdges2Cycles())
db.add_filler(deps_filters_fillers.AutoPackageEdges2Cycles())
db.add_filler(deps_filters_fillers.FiltersFolderFiller(input_folder=os.path.abspath(os.path.join(os.path.dirname(__file__),'data','filters')))) # Checking if some filters are declared in the same folder
db.add_filler(deps_filters_fillers.FiltersFolderFiller()) # Adding filters from the updated list provided in repodepo itself
db.fill_db()
