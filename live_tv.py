import cv2
from time import sleep
import numpy as py
import re
import sys
import os
import urllib.parse
import urllib.request
import multiprocessing
from ffpyplayer.player import MediaPlayer
def live_tv(channel_name,queue):
    m3u8_dict={'aajtak':'https://vidcdn.vidgyor.com/at-origin/liveabr/at-origin/live4/chunks.m3u8',
   'indiatv':'https://live-indiatvnews.akamaized.net/indiatv-origin/liveabr/indiatv-origin/ITV_1_2@199237/chunks.m3u8',
    'abpnews':'https://abp-i.akamaihd.net/hls/live/765529/abphindi/master.m3u8'}
    url = m3u8_dict[channel_name]
    req = urllib.request.Request(url)
    try:
       res = urllib.request.urlopen(req)
    except urllib.error.URLError as q:
            print("m3u8:- "+q.reason)
    else:
       data = res.read()
       data = data.decode('ascii') 
       playlist_obj = [str(x) for x in data.split('\n') if re.search(r'\.ts$',str(x))]
       obj = re.findall('.*\.ts',str(data))
       old_value = (m3u8_dict[channel_name].split('/'))[-1]
       for link_value in playlist_obj:
           link_url = url.replace(old_value,link_value.split('\n')[0])
           req1 = urllib.request.Request(link_url)
           try:
             res1 = urllib.request.urlopen(req1)
           except urllib.error.URLError as q:
              print("ts:- "+q.reason)
           else:
                queue.put(res1.read())
def live(queue):
   while not queue.empty():
      print("writing m3u8 file")
      writing_video(queue.get())
      print("running video")
      running_video()
   print("Done")
   
def writing_video(queue_data):
   with open('live_video.ts','wb') as f:   
      f.write(queue_data)
      f.flush()
      os.fsync(f)
def running_video():
     cap = cv2.VideoCapture('live_video.ts')  
     player = MediaPlayer('live_video.ts')
     if (cap.isOpened()== False):  
           print("Error opening video  file") 
     while(cap.isOpened()): 
        ret, frame = cap.read() 
        audio_frame = player.get_frame()
        if ret == True: 
          cv2.imshow('Frame', frame)  
          if cv2.waitKey(40) & 0xFF == ord('q'): 
            break
        else:  
          pass
     cap.release() 
     cv2.destroyAllWindows()
if __name__ == "__main__":
   queue = multiprocessing.Queue()
   proc1 = multiprocessing.Process(target=live_tv,args=(sys.argv[1],queue))
   proc1.start()
   while queue.empty():
      print("waiting ....")
   else:
     proc2 = multiprocessing.Process(target=live,args=(queue,))
     proc2.start()
     proc1.join()
     proc2.join()
   