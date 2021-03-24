#!/usr/bin/env python3

from ping3 import ping, verbose_ping
from tcp_latency import measure_latency
from mysql.connector import errorcode
from datetime import datetime
import mysql.connector
import iperf3
import sys
import threading, time, os

# Number of test done
global test_number
test_number = 0

# IP address destination
ip = sys.argv[3]

# variable for testing
global upload_troughput
global download_throughput
global latency
global jitter
global loss_rate

upload_troughput = 0
download_throughput = 0
latency = 0
jitter = 0
loss_rate = 0

def listToString(s):  
    
    # initialize an empty string 
    str1 = 0
    
    # traverse in the string   
    for ele in s:  
        str1 += ele   
    
    # return string   
    return str1  

def mysql_insert(now, throughput_upload, throughput_download, latency, jitter, loss_rate):
    mydb = mysql.connector.connect(
        host= "172.17.0.3",
        user="root",
        password="yourpassword",
        database="iperf3_testing",
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()

    sql = "insert into test_performance_%s values (CONVERT_TZ('%s-%s-%s %s:%s:%s','+08:00','+00:00'),%.3f,%.3f,%.3f,%.3f, %.3f)"
    #print(sys.argv[2])
    #print(sql % (sys.argv[2], now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput_upload, throughput_download, latency, jitter, loss_rate))
    #print(now.strftime("%S"))
    mycursor.execute(sql % (sys.argv[2], now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput_upload, throughput_download, latency, jitter, loss_rate))

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

def test_tcp_upload():
    client = iperf3.Client()
    client.duration = 1
    client.server_hostname = ip
    client.port = sys.argv[4]
    client.num_streams = 15
    client.protocol = 'tcp'
    #client.bulksize = 8000
    client.omit = 1
    
    if sys.argv[2] == "mifi_5g_without_mec" :
        print("5g without mec, testing without omitting...")
        client.omit = 0

    global test_number
    global upload_troughput

    print('==========================================================')
    print('Test number %d' %test_number)
    print('==========================================================')
    
    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    
    # get test start time
    now = datetime.now()
    
    
    result = client.run()

    if result.error:
        #print ('Test number is decresead %d' %test_number)
        #test_number -= 1
        print(result.error)
    else:
        test_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print('')
        print('Test completed for Upload:')
        print("  started at                 ",test_time)	
        print('  started at                  {0}'.format(result.time))	
        print('  started at (second)         {0}'.format(result.timesecs))
        #print('  bits transmitted           {0}'.format(result.sent_Mbps))
        #print('  bits received              {0}'.format(result.received_Mbps))
        #print('  loss packet                {0}'.format(result.lost_packets))
        #print('  loss packet peercentage    {0}'.format(result.lost_percent))
        #print('  avg cpu load               {0}%\n'.format(result.local_cpu_total))

        print('==========================================================')

        print('Average transmitted data :')
        #print('  bits per second      (bps)   {0}'.format(result.bps))
        #print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
        print('  Megabits per second  (Mbps)   {0}'.format(result.sent_Mbps))
        #print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
        print('  MegaBytes per second (MB/s)   {0}'.format(result.sent_MB_s))

        print('==========================================================')

        print('Average received data :')    
        print('  Megabits per second  (Mbps)  {0}'.format(result.received_Mbps))
        print('  MegaBytes per second (MB/s)  {0}'.format(result.received_MB_s))
        print('  retransmission done          {0}'.format(result.retransmits))

        print('==========================================================')

        # Put the result on the global variable
        upload_troughput = result.sent_Mbps

def test_tcp_download():
    client = iperf3.Client()
    client.duration = 1
    client.server_hostname = ip
    client.port = sys.argv[4]
    client.num_streams = 15
    client.protocol = 'tcp'
    #client.bulksize = 1470
    client.reverse = True
    client.omit = 1
    
    if sys.argv[2] == "mifi_5g_without_mec" :
        print("5g without mec, testing without omitting...")
        client.omit = 0

    global test_number
    global download_throughput

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    
    # get test start time
    now = datetime.now()
    
    result = client.run()

    if result.error:
        #print ('Test number is decresead %d' %test_number)
        #test_number -= 1
        print(result.error)
    else:
        
        test_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print('')
        print('Test completed for Download:')
        print("  started at                 ",test_time)	
        print('  started at                  {0}'.format(result.time))	
        print('  started at (second)         {0}'.format(result.timesecs))
        #print('  bits transmitted           {0}'.format(result.sent_Mbps))
        #print('  bits received              {0}'.format(result.received_Mbps))
        #print('  loss packet                {0}'.format(result.lost_packets))
        #print('  loss packet peercentage    {0}'.format(result.lost_percent))
        #print('  avg cpu load               {0}%\n'.format(result.local_cpu_total))

        print('==========================================================')

        print('Average transmitted data :')
        #print('  bits per second      (bps)   {0}'.format(result.bps))
        #print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
        print('  Megabits per second  (Mbps)   {0}'.format(result.sent_Mbps))
        #print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
        print('  MegaBytes per second (MB/s)   {0}'.format(result.sent_MB_s))

        print('==========================================================')

        print('Average received data :')    
        print('  Megabits per second  (Mbps)  {0}'.format(result.received_Mbps))
        print('  MegaBytes per second (MB/s)  {0}'.format(result.received_MB_s))
        print('  retransmission done          {0}'.format(result.retransmits))

        print('==========================================================')

        # Put the result on the global variable
        download_throughput = result.sent_Mbps
        

def test_latency():
    global latency

    # Test the RTT first before iperf test
    rtt_list = measure_latency(host= ip, port= 6516 , runs=1, timeout=2.5)
    
    # Making sure tcp latency is working
    while rtt_list[0] == None:
        rtt_list = measure_latency(host=ip, port= 6516, runs=1, timeout=2.5)

    #change from list to float
    latency = float(rtt_list[0])

def test_udp():
    client = iperf3.Client()
    client.duration = 1
    client.server_hostname = ip
    client.port = sys.argv[4]
    client.num_streams = 1
    client.bandwidth = 10000000
    client.bulksize = 1470
    client.protocol = 'udp'
    client.omit = 1

    global test_number
    global jitter
    global loss_rate

    if sys.argv[2] == "mifi_5g_without_mec" :
        print("5g without mec, testing without omitting...")
        client.omit = 1

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))

    # get test start time
    now = datetime.now()

    result = client.run()

    if result.error:
        #print ('Test number is decresead %d' %test_number)
        #test_number -= 1
        print(result.error)
    else:
        test_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print('')
        print('Test completed for UDP:')
        print("  started at                ",test_time)	
        print('  started at                 {0}'.format(result.time))	
        print('  started at (second)        {0}'.format(result.timesecs))

        print('==========================================================')

        print('UDP Test Result :')
        print('  bytes transmitted          {0}'.format(result.bytes))
        print('  jitter (ms)                {0}'.format(result.jitter_ms))
        print('  packets sent               {0}'.format(result.packets))
        print('  loss packet                {0}'.format(result.lost_packets))
        print('  loss packet percentage     {0}'.format(result.lost_percent))
        # print('  avg cpu load       {0}%\n'.format(result.local_cpu_total))

        print('==========================================================')

        print('Average transmitted data :')
        #print('  bits per second      (bps)   {0}'.format(result.bps))
        #print('  Kilobits per second  (kbps)  {0}'.format(result.kbps))
        print('  Megabits per second  (Mbps)  {0}'.format(result.Mbps))
        #print('  KiloBytes per second (kB/s)  {0}'.format(result.kB_s))
        print('  MegaBytes per second (MB/s)  {0}'.format(result.MB_s))

        print('==========================================================')

        # Put the result on the global variable
        jitter = result.jitter_ms
        loss_rate = result.lost_percent
        
def wait():
    print('Testing for %s seconds' % sys.argv[1])
    time.sleep(int(sys.argv[1]))
    print('==========================================================')
    print('Testing duration has finished, exiting program')
    print('==========================================================')
    os._exit(1)

def test_with_threading():
    while 1 :
        test_tcp_upload()

def test_normal():
    global test_number
    global upload_troughput
    global download_throughput
    global latency
    global jitter
    global loss_rate

    print('Testing for %s times' % sys.argv[1])
    while test_number < int(sys.argv[1]) :
        # make all variale 0 first
        upload_troughput = 0
        download_throughput = 0
        latency = None
        jitter = 0
        loss_rate = 0

        test_tcp_download()
        while download_throughput < 200 :
            print ("There is something wrong with download testing, retrying")
            time.sleep(3)
            test_tcp_download()   

        time.sleep(3)

        test_tcp_upload()
        while upload_troughput < 100 :
            print ("There is something wrong with upload testing, retrying")
            time.sleep(3)
            test_tcp_upload()

        time.sleep(3)

        test_latency()    

        test_udp()
        while jitter == 0 :
            print ("There is something wrong with udp testing, retrying")
            time.sleep(3)
            test_udp()

        # get time for mysql input
        now = datetime.now()

        print ("Result is", upload_troughput, download_throughput, latency, jitter, loss_rate)
        mysql_insert(now, upload_troughput, download_throughput, latency, jitter, loss_rate)
        time.sleep(3)
        test_number += 1


# If you want to test using threading
#background = threading.Thread(name = 'test_performance', target = test)
#background.start()
#wait()

test_normal()