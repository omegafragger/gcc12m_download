import os
import csv
import json
import argparse
from tqdm import tqdm

import requests
import multiprocessing as mp
from multiprocessing import Process, Manager


NUM_RECORDS_PER_PROCESS = 2500
NUM_PROCESSES = 400


meta_file_dict = {
    'train': 'Train_GCC-training.tsv',
    'val': 'Validation_GCC-1.1.0-Validation.tsv'
}

# Get the start index for the script. The script will download a million images from the start index.
def get_parser():
    '''
    Get arguments
    '''
    parser = argparse.ArgumentParser(
        description="Args for training parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--start", type=int, dest="start_idx", required=True, help="Start index for the script")
    parser.add_argument("--store_path", type=str, dest="store_path", required=True, help="Path to store images")
    parser.add_argument("--split", type=str, dest="split", required=True, help="Split to find the metadata file: train/val")
    return parser


def download_one_record(record_meta_data, record_id, res_dict, store_path):
    '''
    record_meta_data: contains the link and the text description of the image for the link
    record_id: record id will be the image id of the stored image
    res_dict: Dictionary to indicate if record failed or succeeded.
    store_path: Path to store the image
    '''
    
    link = record_meta_data[0]
    image_desc = record_meta_data[1]
    
    try:
        img_data = requests.get(link, timeout=10).content
        with open(os.path.join(store_path, f'image_{record_id}.jpg'), 'wb') as handler:
            handler.write(img_data)
        res_dict[record_id] = 1
    except Exception as e:
        res_dict[record_id] = 0
    

def download_records_1_process(meta_dict, start_idx, num_records, res_dict, store_path):
    '''
    meta_dict: dictionary of meta data
    start_idx: start index of download
    num_records: number of records to be downloaded
    res_dict: result dictionary containing information of how many records were downloaded
    store_path: Path to store images
    '''
    for idx in range(start_idx, start_idx + num_records):
        if idx in meta_dict.keys():
            record_meta_data = meta_dict[idx]
            download_one_record(record_meta_data, idx, res_dict, store_path)


def download_records_multi_process(meta_dict, start_idx, num_records_per_process, num_processes, res_dict, store_path):
    '''
    meta_dict: dictionary of meta data
    start_idx: start index of download for all processes
    num_records_per_process: number of records to be downloaded per process
    num_processes: number of processes to be launched
    res_dict: result dictionary containing information of which records were stored correctly
    store_path: Path to store images
    '''
    moving_idx = start_idx
    proc_list = []
    
    print ('Starting processes...')
    for p in tqdm(range(num_processes)):
        proc = Process(target=download_records_1_process, args=(meta_dict, moving_idx, num_records_per_process, res_dict, store_path))
        moving_idx = moving_idx + num_records_per_process
        proc.start()
        proc_list.append(proc)
    
    print ('Joining processes...')
    for proc in tqdm(proc_list):
        proc.join()


def main():
    parser = get_parser()
    args = parser.parse_args()
    start_idx = args.start_idx
    store_path = args.store_path
    split = args.split

    cc12m_dict = {}

    with open(meta_file_dict[split]) as file:
        tsv_file = csv.reader(file, delimiter="\t")

        for i, line in tqdm(enumerate(tsv_file)):
            cc12m_dict[i] = line

    manager = Manager()
    shared_res_dict = manager.dict()

    download_records_multi_process(cc12m_dict, start_idx, NUM_RECORDS_PER_PROCESS, NUM_PROCESSES, shared_res_dict, store_path)

    final_res_dict = {}

    for k in shared_res_dict.keys():
        final_res_dict[k] = shared_res_dict[k]

    with open(f'res_download_{start_idx}.json', 'w+') as fp:
        json.dump(final_res_dict, fp)


if __name__=='__main__':
    main()