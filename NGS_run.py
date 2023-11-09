import os
import gzip
import subprocess
import shutil

def process_subfolders(top_folder):
    # Check if the specified path exists
    if not os.path.exists(top_folder):
        print("The specified folder does not exist.")
        return

    # Iterate through subfolders
    for subfolder in os.listdir(top_folder):
        subfolder_path = os.path.join(top_folder, subfolder)

        # Check if the item is a directory
        if os.path.isdir(subfolder_path):
            fastq_file = os.path.join(subfolder_path, f'{subfolder}.fastq')

            # Iterate through files in the subfolder
            with open(fastq_file, 'wb') as output_file:
                for file in os.listdir(subfolder_path):
                    if file.endswith('.fastq.gz'):
                        file_path = os.path.join(subfolder_path, file)

                        # Extract and write the content of the .fastq.gz files
                        with gzip.open(file_path, 'rb') as input_file:
                            output_file.write(input_file.read())

            print(f'Created {fastq_file} in {subfolder}')

def move_fastq_files_to_all_reads(top_folder):
    
    all_reads_folder = os.path.join(top_folder, 'all_reads')

    # Create the "all_reads" subfolder if it doesn't exist
    if not os.path.exists(all_reads_folder):
        os.mkdir(all_reads_folder)

        
    # Move the created .fastq files to the "all_reads" subfolder
    for subfolder in os.listdir(top_folder):
        subfolder_path = os.path.join(top_folder, subfolder)

        if os.path.isdir(subfolder_path):
            fastq_file = os.path.join(subfolder_path, f'{subfolder}.fastq')
            
            if os.path.exists(fastq_file):
                new_path = os.path.join(all_reads_folder, f'{subfolder}.fastq')
                os.rename(fastq_file, new_path)
                print(f'Moved {fastq_file} to "all_reads" folder')

def run_NGSpeciesID(top_folder, flowcell_name):
    all_reads_folder = os.path.join(top_folder, 'all_reads')
    
    # Change the working directory to the "all_reads" folder
    os.chdir(all_reads_folder)

    for file in os.listdir(all_reads_folder):
        if file.endswith(".fastq"):
            bn = os.path.splitext(file)[0]
            try:
                subprocess.run([
                    "NGSpeciesID",
                    "--ont",
                    "--consensus",
                    "--t", "12",
                    "--q", "8",
                    "--medaka",
                    "--fastq", file,
                    "--outfolder", f"{flowcell_name}_{bn}"
                ], check=True)
                print(f"NGSpeciesID successfully completed for {file}.")
            except subprocess.CalledProcessError:
                print(f"Error during NGSpeciesID for {file}.")

def move_consensus_folders(top_folder, flowcell_name):
    all_reads_folder = os.path.join(top_folder, 'all_reads')
    consensus_folder = os.path.join(top_folder, 'consensus_folder')
    # Create the "consensus_folder" subfolder if it doesn't exist
    if not os.path.exists(consensus_folder):
        os.mkdir(consensus_folder)   
    
    # Change the working directory to the "all_reads" folder
    os.chdir(all_reads_folder)
    # Move the subfolders to the "consensus_folder" subfolder
    for subfolder in os.listdir(all_reads_folder):
        subfolder_path = os.path.join(all_reads_folder, subfolder)
        if subfolder.startswith(f"{flowcell_name}"):   
            if os.path.exists(subfolder):
                new_path = os.path.join(top_folder, consensus_folder, subfolder)
                os.rename(subfolder_path, new_path)
                print(f'Moved {subfolder}s to "consensus_folder" folder')

def move_raw_reads_folders(top_folder):
    raw_reads = os.path.join(top_folder, 'raw_reads')
    # Create the "raw_reads" subfolder if it doesn't exist
    if not os.path.exists(raw_reads):
        os.mkdir(raw_reads)   
    
    # Move the subfolders to the "raw_reads" subfolder
    for subfolder in os.listdir(top_folder):
        subfolder_path = os.path.join(top_folder, subfolder)
        if subfolder.startswith(f"barcode"):   
            if os.path.exists(subfolder_path):
                new_path = os.path.join(top_folder, raw_reads, subfolder)
                os.rename(subfolder_path, new_path)
                print(f'Moved {subfolder}s to "raw_reads_folder" folder')

def rename_files_and_move(top_folder):
    # Create the "renamed" folder if it doesn't exist
    renamed_folder = os.path.join(top_folder, 'renamed')
    if not os.path.exists(renamed_folder):
        os.mkdir(renamed_folder)

    # Iterate through the "Barcode" folders
    for barcode_folder in os.listdir(os.path.join(top_folder, "consensus_folder")):
        if os.path.isdir(os.path.join(top_folder, "consensus_folder", barcode_folder)):
            # Extract the Barcode name
            barcode_name = barcode_folder

            # Iterate through the "medaka_cl_id" folders
            for medaka_folder in os.listdir(os.path.join(top_folder, "consensus_folder", barcode_folder)):
                if os.path.isdir(os.path.join(top_folder, "consensus_folder", barcode_folder, medaka_folder)):
                    # Extract the medaka folder name
                    medaka_name = medaka_folder

                    # Define the new name for the "consensus.fasta" file
                    new_filename = f"{barcode_name}_{medaka_name}.fasta"

                    # Check if the "consensus.fasta" file exists in the medaka folder
                    consensus_path = os.path.join(top_folder, "consensus_folder", barcode_folder, medaka_folder, "consensus.fasta")
                    if os.path.exists(consensus_path):
                        # Move the file to the "renamed" folder
                        renamed_path = os.path.join(renamed_folder, new_filename)
                        os.rename(consensus_path, renamed_path)
                        print(f"Renamed: consensus.fasta to {new_filename} and moved to {renamed_folder}")
                    else:
                        print(f"consensus.fasta not found in {consensus_path}")

def replace_fasta_ids_in_folder(top_folder):
    # Define renamed and modified paths
    # Create the "modified" folder if it doesn't exist
    renamed_folder = os.path.join(top_folder, 'renamed')
    modified_folder = os.path.join(top_folder, 'modified')
    if not os.path.exists(modified_folder):
        os.mkdir(modified_folder)

    # Loop through the files in the input folder
    for filename in os.listdir(renamed_folder):
        if filename.endswith('.fasta'):
            # Construct the full file paths
            fasta_file = os.path.join(renamed_folder, filename)
            output_file = os.path.join(modified_folder, f'{filename.split(".")[0]}_modified.fasta')
            new_name = filename.split(".")[0]
            with open(fasta_file, 'r') as infile:
                with open(output_file, 'w') as outfile:
                    for line in infile:
                        if line.startswith('>'):
                            # Extract the existing ID without modifying it
                            existing_id = line.strip()

                            # Replace only the ID part while keeping the rest of the line intact
                            line = f'>{new_name}_{existing_id}\n'
                        outfile.write(line)                      
                      
def remove_folder(top_folder):
    renamed_folder = os.path.join(top_folder, 'renamed')

    if os.path.exists(renamed_folder) and os.path.isdir(renamed_folder):
        try:
            shutil.rmtree(renamed_folder)  # Removes the directory and its contents
            print(f"Folder '{renamed_folder}' and its contents have been successfully removed.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"The folder '{renamed_folder}' does not exist.")
      
def concatenate(top_folder, output_file_name):

    modified_folder = os.path.join(top_folder, 'modified')
    concat_file_path = os.path.join(top_folder, output_file_name)
     
    # Iterate through subfolders
    for file in os.listdir(modified_folder):
        with open(concat_file_path, 'w') as output_file:
                for file in os.listdir(modified_folder):
                    if file.endswith('.fasta'):
                        file_path = os.path.join(modified_folder, file)
                        # Read the content of the .fasta file and write it to the concatenated file
                        with open(file_path, 'r') as input_file:
                            output_file.write(input_file.read())
    print(f'Concatenated .fasta files from the "modified" folder to {concat_file_path}.')


if __name__ == '__main__':
    top_folder = input("Enter the top-level folder path: \n")
    flowcell_name = input("Enter the flowcell name: \n")
    output_file_name = 'all_concatenate.fasta'
    process_subfolders(top_folder)
    move_fastq_files_to_all_reads(top_folder)
    run_NGSpeciesID(top_folder, flowcell_name)
    move_consensus_folders(top_folder, flowcell_name)
    move_raw_reads_folders(top_folder)
    rename_files_and_move(top_folder)
    replace_fasta_ids_in_folder(top_folder)
    remove_folder(top_folder)
    concatenate(top_folder, output_file_name)