SET vlc="C:\Program Files (x86)\VideoLAN\VLC\vlc.exe"

:: creates filename with current date(y-m-d_H-M-S)
:: 2 seconds delay filename to first frame
SET datetime=%date:~-4%-%date:~3,2%-%date:~0,2%_%time:~0,2%-%time:~3,2%-%time:~6,2%
:: creates current time(y-m-d_H:M:S) for stream
SET sfilter="marq{marquee='%%y-%%m-%%d_%%H:%%M:%%S',position=6,size=25}"

:: 12921
SET file2=C:\\Users\\Paul Pasler\\Desktop\\%datetime%_face.mp4
SET cam1="Logitech HD Webcam C525"
SET mic1="Mikrofon (HD Webcam C525)"

:: 12114
SET file1=C:\\Users\\Paul Pasler\\Desktop\\%datetime%_drive.mp4
SET cam2="Logitech HD Webcam C525 #1"
SET mic2=none

start "cam1" %vlc% dshow:// :dshow-vdev=%cam1% :dshow-adev=%mic1% --sout "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100,sfilter=%sfilter%}:file{dst=%file1%,no-overwrite}"
start "cam2" %vlc% dshow:// :dshow-vdev=%cam2% :dshow-adev=%mic2% --sout "#transcode{vcodec=h264,acodec=mpga,ab=128,channels=2,samplerate=44100,sfilter=%sfilter%}:file{dst=%file2%,no-overwrite}"