#!/bin/bash
pwd
ls
# untar your Python installation
tar -xzf python.tar.gz
tar -xzf working.tar.gz
# make sure the script will use your Python installation, 
# and the working directory as it's home location
export PATH=$(pwd)/python/bin:$PATH
mkdir home
export HOME=$(pwd)/home
# run your script
cp -r chtc/ generating-categories
cd generating-categories/Experiments/cogpsych-code/
python global_model_gridsearch_CHTC.py $1


#tar the pickles
tar -czvf pickles$1.tar.gz pickles/

#Move it to main directory
cd ~
cd ..
mv generating-categories/Experiments/cogpsych-code/pickles$1.tar.gz pickles$1.tar.gz
ls