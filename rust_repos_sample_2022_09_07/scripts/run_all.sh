#!/bin/bash

set -ex

########## Getting script folder to cd into it
########## from https://stackoverflow.com/questions/59895/how-do-i-get-the-directory-where-a-bash-script-is-located-from-within-the-script
SOURCE=${BASH_SOURCE[0]}
while [ -L "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )
  SOURCE=$(readlink "$SOURCE")
  [[ $SOURCE != /* ]] && SOURCE=$DIR/$SOURCE # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR=$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )




########## Execution

(cd $DIR;

if [ -z $(ls ../dumps/sqlite/*.db) ]
then
	python3 generate_dataset.py;
	python3 export_filters_bots.py;
else
	echo 'SQLite dump present, skipping generate_dataset'
fi

python3 generate_additional_CSV.py;

########## Executing example notebooks if necessary
export NB_FOLDER="../examples/notebooks";
NB_LIST=$(cd $NB_FOLDER; ls *.ipynb)
for NB_FILE in $NB_LIST
do
export NB_NAME=$(echo "$NB_FILE" | rev | cut -f 2- -d '.' | rev)
	if [[ ! -f $NB_FOLDER/$NB_NAME.html ]]
	then
		jupyter nbconvert --to notebook --execute $NB_FOLDER/$NB_NAME.ipynb --output $NB_NAME.ipynb
		jupyter nbconvert --to html $NB_FOLDER/$NB_NAME.ipynb --output $NB_NAME.html
	fi
done

python3 globalstats.py;

##### Exporting the dataset
python3 export_dataset.py;

########## Executing basic_plots notebook if necessary
export NB_FOLDER='../statistics'
export NB_NAME='basic_plots'
if [[ ! -f $NB_FOLDER/$NB_NAME.html ]]
then
	jupyter nbconvert --to notebook --execute $NB_FOLDER/$NB_NAME.ipynb --output $NB_NAME.ipynb
	jupyter nbconvert --to html $NB_FOLDER/$NB_NAME.ipynb --output $NB_NAME.html
fi


python3 comparison_ghtorrent.py;

)