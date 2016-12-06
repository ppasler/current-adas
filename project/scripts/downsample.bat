SET vlc="C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

SET inpt=E:\\thesis\\experiment\\1\\2016-12-05_14-23-55_drive.mp4
SET outpt=E:\\thesis\\experiment\\1\\test.mp4

%vlc% -I dummy -vvv %inpt% --sout=#transcode{vcodec=h264,scale=0.75,acodec=mp4a,ab=192,channels=2,deinterlace}:standard{access=file,mux=ts,dst=%outpt%} vlc://quit