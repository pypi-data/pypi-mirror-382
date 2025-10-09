import os
import zipfile
import argparse
import SoccerNet
from SoccerNet.Downloader import SoccerNetDownloader

parser = argparse.ArgumentParser(
    description='Prepare data for ball pass and drive action spotting.')

parser.add_argument('--dataset_dir', type=str,
                    help="Path for dataset directory ", default="/data_pool_1/sn-ballaction-24/")
parser.add_argument('--password_videos','-p', type=str,
                    help="Password to videos from the NDA")
args = parser.parse_args()

list_splits = ["train", "valid", "test", "challenge"]

# Download zipped folder per split
mySoccerNetDownloader = SoccerNetDownloader(LocalDirectory=args.dataset_dir)
mySoccerNetDownloader.downloadDataTask(task="spotting-ball-2024",
                                       split=list_splits,
                                       password=args.password_videos)

