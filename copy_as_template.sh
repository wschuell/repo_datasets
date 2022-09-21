#!/bin/bash

set -e
set -x

echo 'Source dataset:'

read SOURCE_DATASET

if [[ ! -d $SOURCE_DATASET ]]
 then echo "$SOURCE_DATASET not found"; exit 1;
fi

echo 'Destination dataset:'

read DEST_DATASET

if [[ ! -d $DEST_DATASET ]]
 then
  echo "Creating dataset $DEST_DATASET"
 mkdir -p $DEST_DATASET
 mkdir -p $DEST_DATASET/statistics
 mkdir -p $DEST_DATASET/scripts/data/filters
 mkdir -p $DEST_DATASET/examples/notebooks
 mkdir -p $DEST_DATASET/examples/preprocessed
 for filepath in README.md \
                 statistics/basic_plots.ipynb \
                 examples/notebooks/demo1_dependency_network.ipynb \
                 examples/notebooks/demo2_usage.ipynb \
                 examples/notebooks/demo3_collaboration_network.ipynb \
                 scripts/comparison_ghtorrent.py \
                 scripts/export_dataset.py \
                 scripts/export_filters_bots.py \
                 scripts/generate_additional_CSV.py \
                 scripts/generate_dataset.py \
                 scripts/globalstats.py \
                 scripts/set_parameters.py \
                 scripts/run_all.sh \
                 scripts/data/bots.csv \
                 scripts/data/tables_filter.yml \
                 scripts/data/filters/filtered_packageedges.csv \
                 scripts/data/filters/filtered_packages.csv \
                 scripts/data/filters/filtered_repos.csv \
                 scripts/data/filters/filtered_repoedges.csv
  do
   cp $SOURCE_DATASET/$filepath $DEST_DATASET/$filepath
  done

 else
  echo "Dataset $DEST_DATASET already exists"; exit 1;
fi
