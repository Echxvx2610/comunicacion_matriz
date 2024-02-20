from file_monitor import start_csv_observer
import time
thread = start_csv_observer()



#funcion principal
for i in range(0, 100):
    print(i)
    time.sleep(1)



        
