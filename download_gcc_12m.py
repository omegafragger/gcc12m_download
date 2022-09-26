import os
import csv
import argparse
from tqdm import tqdm

import requests
import multiprocessing as mp
from multiprocessing import Process, Manager


cc12m_dict = {}


# Get the start index for the script. The script will download a million images from the start index.
parser = argparse.ArgumentParser(
    description="Args for training parameters", formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--start", type=int, dest="start_idx", required=True, help="Start index for the script")
parser.add_argument("--store_path", type=str, dest="store_path", required=True, help="Path to store images")

args = parser.parse_args()
start_idx = args.start_idx
store_path = args.store_path


with open("cc12m.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")

    for i, line in tqdm(enumerate(tsv_file)):
        cc12m_dict[i] = line



def download_one_record(record_meta_data, record_id, res_dict):
    '''
    record_meta_data: contains the link and the text description of the image for the link
    record_id: record id will be the image id of the stored image
    '''
    
    link = record_meta_data[0]
    image_desc = record_meta_data[1]
    
    try:
        img_data = requests.get(link, timeout=10).content
        with open(os.path.join(store_path, f'image_{record_id}.jpg', 'wb')) as handler:
            handler.write(img_data)
        res_dict[record_id] = 1
    except:
        res_dict[record_id] = 0
    

def download_records_1_process(meta_dict, start_idx, num_records, res_dict):
    '''
    meta_dict: dictionary of meta data
    start_idx: start index of download
    num_records: number of records to be downloaded
    res_dict: result dictionary containing information of how many records were downloaded
    '''
    
    for idx in range(start_idx, start_idx + num_records):
        if idx in meta_dict.keys():
            record_meta_data = meta_dict[idx]
            download_one_record(record_meta_data, idx, res_dict)


manager = Manager()
shared_res_dict = manager.dict()

def download_records_multi_process(meta_dict, start_idx, num_records_per_process, num_processes, res_dict):
    '''
    meta_dict: dictionary of meta data
    start_idx: start index of download for all processes
    num_records_per_process: number of records to be downloaded per process
    num_processes: number of processes to be launched
    res_dict: result dictionary containing information of which records were stored correctly
    '''
    moving_idx = start_idx
    proc_list = []
    
    print ('Starting processes...')
    for p in tqdm(range(num_processes)):
        proc = Process(target=download_records_1_process, args=(meta_dict, moving_idx, num_records_per_process, res_dict))
        moving_idx = moving_idx + num_records_per_process
        proc.start()
        proc_list.append(proc)
    
    print ('Joining processes...')
    for proc in tqdm(proc_list):
        proc.join()

num_records_per_process = 500
num_processes = 2000

download_records_multi_process(cc12m_dict, start_idx, num_records_per_process, num_processes, shared_res_dict)

final_res_dict = {}

for k in shared_res_dict.keys():
    final_res_dict[k] = shared_res_dict[k]

import json

with open(f'res_download_{start_idx}.json', 'w+') as fp:
    json.dump(final_res_dict, fp)
