cd E:\current-adas\project\code

SET vlc="C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

:: creates filename with current date(y-m-d_H-M-S)
:: 2 seconds delay filename to first frame
SET datetime=%date:~-4%-%date:~3,2%-%date:~0,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
:: creates current time(y-m-d_H:M:S) for stream
SET sfilter="marq{marquee='%%y-%%m-%%d_%%H:%%M:%%S',position=6,size=10}"

SET file1=data\\%datetime%.mp4
SET cam1="Integrated Camera"
SET mic1=none

start "emotiv" python src\http_eeg_data_provider.py
start "cam1" %vlc% dshow:// :dshow-vdev=%cam1% :dshow-adev=%mic1% --sout "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100,sfilter=%sfilter%}:file{dst=%file1%,no-overwrite}"