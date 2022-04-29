kill -9 $(ps -aux | grep motor | awk '{print $2}')
kill -9 $(ps -aux | grep mm-delay | awk '{print $2}')
kill -9 $(ps -aux | grep mm-link | awk '{print $2}')