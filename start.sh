#!/bin/bash
#!/bin/sh
$(pkill -f "gphoto2")
while true
do
	npy=$(pgrep -c python3)	
	if [ "$npy" -lt 1 ]
	then 
		python3 main.py
	fi
	sleep 3
done