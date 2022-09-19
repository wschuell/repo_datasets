
import repodepo as rd
from repodepo.fillers import generic,github_rest,commit_info,crates,julia,github_gql,gitlab_gql,meta_fillers,deps_filters_fillers,bot_fillers
import os
import psycopg2
import time



######## PARAMETERS ########

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
					clones_folder = clones_folder,
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

# package_limit = 100 # Set a package limit to build a sample dataset, from the N first packages by id. If set to None, no limit.
package_limit = None # Set a package limit to build a sample dataset, from the N first packages by id. If set to None, no limit.


workers = 4 # Number of parallel threads for querying the github APIs

print('Make sure you have a github API key (with permission read:user for GraphQL) in $HOME/.repo_tools/github_api_keys.txt. Continuing in 3s.')
print('Make sure you have a gitlab API key in $HOME/.repo_tools/gitlab_api_keys.txt. Continuing in 3s.')
time.sleep(3)


db = rd.repo_database.Database(**db_conninfo)

db.init_db()
db.add_filler(generic.SourcesFiller(source=['GitHub','Gitlab'],source_urlroot=['github.com','gitlab.com']))
db.add_filler(crates.CratesFiller(package_limit=package_limit,**db_crates_conninfo)) # Filling in informations from a crates database: packages, urls, versions, dependencies, downloads

db.add_filler(generic.DLSamplePackages(nb_packages=100)) # Trims the list of packages to the top most downloaded

db.add_filler(generic.RepositoriesFiller()) # Parses the URLs of the packages to attribute them to the available sources (github.com and gitlab.com)
db.add_filler(generic.SourcesAutoFiller()) # Checks for unattributed sources in URL that are valid git platforms
db.add_filler(generic.RepositoriesFiller()) # Completes the first call by integrating the new sources

db.add_filler(github_gql.ForksGQLFiller(workers=workers))
db.add_filler(generic.ClonesFiller()) # Clones after forks to have up-to-date repo URLS (detect redirects)
db.add_filler(commit_info.CommitsFiller()) # Commits after forks because fork info needed for repo commit ownership ran at the end.
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
db.add_filler(github_gql.CommitCommentsGQLFiller(workers=workers)) # Integrates commit comments reactions
db.add_filler(github_gql.CompleteIssuesGQLFiller(workers=workers)) # Integrates reactions, comments, comment reactions and labels
db.add_filler(github_gql.CompletePullRequestsGQLFiller(workers=workers)) # Integrates reactions, comments, comment reactions and labels
db.add_filler(gitlab_gql.CompleteIssuesGQLFiller(workers=workers)) # Integrates reactions, comments, comment reactions and labels
db.add_filler(gitlab_gql.CompletePullRequestsGQLFiller(workers=workers)) # Integrates reactions, comments, comment reactions and labels
db.add_filler(generic.RepoCommitOwnershipFiller())
db.add_filler(github_gql.RepoCreatedAtGQLFiller(workers=workers))
db.add_filler(gitlab_gql.RepoCreatedAtFiller(workers=workers))
db.add_filler(github_gql.UserCreatedAtGQLFiller(workers=workers))
db.add_filler(github_gql.UserOrgsGQLFiller(workers=1))
db.add_filler(github_gql.RepoLanguagesGQLFiller(workers=workers)) # Filling in repository language shares (approximation made directly by GitHub)
db.add_filler(github_gql.UserLanguagesGQLFiller(workers=workers)) # Compiling an approximation of user contributions in each language over a time period (default one year up to query time)
db.add_filler(meta_fillers.MetaBotFiller()) # wrapping several techniques to flag bots and invalid identities
db.add_filler(deps_filters_fillers.AutoRepoEdges2Cycles())
db.add_filler(deps_filters_fillers.AutoPackageEdges2Cycles())
db.add_filler(deps_filters_fillers.FiltersFolderFiller(input_folder=os.path.abspath(os.path.join(os.path.dirname(__file__),'data','filters')))) # Checking if some filters are declared in the same folder
db.add_filler(deps_filters_fillers.FiltersFolderFiller()) # Adding filters from the updated list provided in repodepo itself

# POTENTIALLY BLOCKING STEPS NEEDING MANUAL INPUT
db.add_filler(bot_fillers.BotsManualChecksFiller()) # listing accounts to be checked manually for being bots/invalid
db.add_filler(deps_filters_fillers.DepsManualChecksFiller()) # blocking if there are non-flagged cycles in the dependency network


db.fill_db()
