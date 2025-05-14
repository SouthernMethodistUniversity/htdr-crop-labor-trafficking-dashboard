#!/bin/bash

#SBATCH -A tuev_oit_rts_star_0001
#SBATCH -J Extract_TIF_Data       # job name to display in squeue
#SBATCH -o output-%j.txt    # standard output file
#SBATCH -e error-%j.txt     # standard error file
#SBATCH -p dev              # requested partition
#SBATCH -t 120              # maximum runtime in minutes
#SBATCH --mem=10G           # memory in GB

#SPECIFY STARTING DIRECTORY
#SBATCH -D /users/apetmecky/hmtrfkproj

#SBATCH --array=0-300


module load conda
conda activate myenv





# Path to your Python script
input_file="./filepaths.txt"
python_script="./HPC_SCRIPT.py"
#arg1="Hello"
# Execute the Python script
#python3 "$python_script" "$arg1"

python3 "$python_script" "$SLURM_ARRAY_TASK_ID"


#while read -r line; do
#    # Pass each line as an argument to the Python script
#    #python3 "$python_script" "$line"
#    python3 "$python_script" "$SLURM_ARRAY_TASK_ID"
#done < "$input_file"