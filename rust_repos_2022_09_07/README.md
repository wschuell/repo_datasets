# README

This README lists and details the files to be found in the release of the `rust_repos_sample` dataset.
They are organized into different categories:
 - the dataset itself
 - pre-processed CSV files ready for immediate researcher use and demonstration Jupyter notebooks
 - general statistics about the dataset as yml files
 - scripts to reproduce the dataset, the processed CSV files and the statistics

## Overview of the folder

```
.
├── README.md
├── dumps
│   ├── ERdiagram.png
│   ├── sqlite
│   │   └── rust_repos_sample.db
│   └── postgresql
│       ├── script.sh
│       ├── schema.sql
│       ├── import.sql
│       └── data
│           ├── <table1>.csv
│           ├── <table2>.csv
│          ...
│           └── <tableN>.csv
├── examples
│   ├── preprocessed
│   │   ├── usage.csv
│   │   ├── contributions.csv
│   │   └── dependencies.csv
│   └── notebooks
│       ├── demo1_dependency_network.ipynb
│       ├── demo1_dependency_network.html
│       ├── demo2_usage.ipynb
│       ├── demo2_usage.html
│       ├── demo3_collaboration_network.ipynb
│       └── demo3_collaboration_network.html
├── statistics
│   ├── basic_plots.ipynb
│   ├── basic_plots.html
│   ├── global_stats.yml
│   └── ghtorrent_comparison.yml
└── scripts
    ├── data
    │   ├── bots.csv
    │   ├── tables_filter.yml
    │   └── filters
    │       ├── filtered_packages.csv
    │       ├── filtered_packageedges.csv
    │       ├── filtered_repos.csv
    │       └── filtered_repoedges.csv
    ├── generate_dataset.py
    ├── export_dataset.py
    ├── export_filters_bots.py
    ├── generate_additional_CSV.py
    ├── globalstats.py
    ├── comparison_ghtorrent.py
    └── set_parameters.py
```

## Description of the files

### Dataset dumps

The dataset is released in two formats, in the folder `dumps`:
 - A ready-to-use SQLite file `sqlite/rust_repos_sample.db`
 - Files to reproduce the database in PostgreSQL:
  - `postgresql/script.sh` A wrapper bash script to call `schema.sql` and `import.sql` while asking for database credentials (consider using a `$HOME/.pgpass` file, see [the official documentation][1]) 
  - `postgresql/schema.sql` to create the structure in your empty database 
  - `postgresql/import.sql` to populate it
  - `postgresql/data/<table>.csv` CSV files (one per table) used in the `import.sql` script

One can alternatively use the CSV files from the PostgreSQL dump directly, for example by importing them into pandas dataframes.

### Examples: Pre-processed CSV files and Jupyter notebooks

We provide three pre-processed CSV files: 
- `contributions.csv` - counting monthly snapshots of contributors to each repo, including the number of commits made.
- `dependencies.csv` - containing monthly snapshots of the repo-level dependency networks.
- `usage.csv` - containing monthly snapshots of repo usage/success statistics including downloads and stars.
To demonstrate how to use these CSV files, we include three Jupyter notebooks which read in the data using Pandas and carry out rudimentary descriptive analyses.

### Statistics

We provide detailed statistics about the dataset in the form of a yml file `global_stats.py`.

We also provide in the same format a comparison with the latest [GHTorrent SQL dataset][5], in the file `ghtorrent_comparison.yml`. For the comparison, only elements previous to the end timestamp of the GHTorrent database (01/06/2019 00:00:00) are considered, and corresponding to repositories that were clonable at the time of dataset construction.

The numbers used in the article are extracted from these files.

We provide an additional notebook with basic plots of time evolution of different measures, as well as the distribution of Rust usage share (compared to other languages) within repositories and global user habits on GitHub. 

### Scripts

To run the Python scripts, you need the library `repodepo` available [here][2].
The specific commit or version used is mentioned in the last section of this document.

To run the dataset collection, you need API keys for GitHub and Gitlab. For GitHub, `read:user` needs to be granted to use the GraphQL API.
API keys can be put in environment variables (one key for each platform) `REPOTOOLS_<GITHUB/GITLAB>_API_KEY`,
Or alternatively listed in `$HOME/.repodepo/<github/gitlab>_api_keys.txt`

- **Regenerate the dataset `generate_dataset.py`:** This script regenerates the database (not anonymized, and with additional tables). One can choose to regenerate it in SQLite or in PostgreSQL through the parameter `db_type` ("sqlite" or "postgres" -- default is PostgreSQL). You will need API keys for both GitHub and Gitlab, as well as an already setup `crates.io` database from one of their dumps available [here][3]. It will need about 150GB space (more over time) to locally clone the repositories, and a few days to go through all the necessary queries. You may need to adapt the connection settings to fit yours (database name, port, host, user).
- **Export/dump the dataset `export_dataset.py`:** This script exports the dataset to another PostgreSQL database (empty), anonymizes it, cleans it (removing some tables and nullifying some attributes), and dumps it in both formats used in this folder. You may need to adapt the connection settings to fit yours (database name, port, host, user).
- **Export the bots and dependency links filtered in the dataset `export_filters_bots.py`:** This script exports the bots and dependency filters used in the dataset in a readable/reusable format.
- **Regenerate the dataset `generate_additional_CSV.py`:** This script generates the CSV files used in the notebooks. For more information/for generating your own variants you can have a look at the file [`repodepo/getters/combined_getters.py`][4]. You may need to adapt the connection settings to fit yours (database name, port, host, user).
- **Global Statistics `globalstats.py`:** This script generates the detailed statistics about the collected dataset. You may need to adapt the connection settings to fit yours (database name, port, host, user).
- **Compute statistics to compare to GHTorrent `comparison_ghtorrent.py`:** This script needs an available PostgreSQL instance of the GHTorrent SQL version. See [here][5] to download dumps. You may need to adapt the connection settings to fit yours (database name, port, host, user).
- **Set the parameters `set_parameters.py`:** This script propagates database connection information to all other scripts, just a shortcut if you wish to have different values than the default.

In the data folder, one can additionally find `table_filters.yml`, a list of which tables and columns to keep from the original DB structure as defined at data collection. This list is used in the script `export_dataset.py`.

## Comments specific to this dataset release

The version of `repodepo` used to produce this folder is [softwareversion], corresponding to commit [softwarecommit].

The date to be considered as an upper bound for validity of the dataset is: [datasetdate]
It corresponds to the timestamp of the database dump of `crates.io` that has been used.






[1]: https://www.postgresql.org/docs/current/libpq-pgpass.html
[2]: https://github.com/wschuell/repodepo
[3]: https://crates.io/data-access
[4]: https://github.com/wschuell/repodepo/blob/master/repodepo/getters/combined_getters.py
[5]: https://ghtorrent.org/downloads.html


[softwareversion]: 0.1.0
[softwarecommit]: 4daeaa608b907c87c6ffad820c877d26af9a2366
[datasetdate]: 2022-03-14
