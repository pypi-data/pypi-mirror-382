import SoccerNet
from SoccerNet.Downloader import SoccerNetDownloader
import os

mySoccerNetDownloader=SoccerNetDownloader(LocalDirectory=os.getcwd())

mySoccerNetDownloader.downloadGames(files=["Labels-v2.json"], split=["train","valid","test"])
