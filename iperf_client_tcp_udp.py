#!/usr/bin/env python3

from ping3 import ping, verbose_ping
from tcp_latency import measure_latency
from mysql.connector import errorcode
from datetime import datetime
import mysql.connector
import iperf3
import sys
import threading, time, os

test_number =  1
finish = False

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
        host="140.118.122.120",
        user="root",
        password="fihdan",
        database="test_grafana",
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

    global test_number
    test_number += 1

def test_tcp_upload():
    client = iperf3.Client()
    client.duration = 5
    client.server_hostname = '140.118.122.120'
    client.port = 5201
    client.num_streams = 15
    client.protocol = 'tcp'
    client.omit = 1

    print('==========================================================')
    print('Test number %d' %test_number)
    print('==========================================================')
    
    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    
    # get test start time
    now = datetime.now()
    

    # Test the RTT first before iperf test
    rtt_list = measure_latency(host='140.118.122.120', port=5201, runs=1, timeout=2.5)

    while rtt_list[0] == None:
        rtt_list = measure_latency(host='140.118.122.120', port=client.port, runs=1, timeout=2.5)

    #change from list to float
    rtt = float(rtt_list[0])
    
    result = client.run()

    if result.error:
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

        print("  Latency to target in ms is %.3f ms" %rtt)

        print('==========================================================')

        test_tcp_download(result.sent_Mbps, rtt)

def test_tcp_download(throughput_upload, rtt):
    client = iperf3.Client()
    client.duration = 5
    client.server_hostname = '140.118.122.120'
    client.port = 5201
    client.num_streams = 15
    client.protocol = 'tcp'
    client.reverse = True
    client.omit = 1

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    
    # get test start time
    now = datetime.now()
    
    result = client.run()

    if result.error:
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

        test_udp(throughput_upload, result.sent_Mbps, rtt)

def test_udp(throughput_upload, throughput_download, rtt):
    client = iperf3.Client()
    client.duration = 10
    client.server_hostname = '140.118.122.120'
    client.port = 5201
    client.num_streams = 1
    client.bandwidth = 10000000
    client.bulksize = 1470
    client.protocol = 'udp'
    client.omit = 1

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))

    # get test start time
    now = datetime.now()

    result = client.run()

    if result.error:
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

        mysql_insert(now, throughput_upload, throughput_download, rtt, result.jitter_ms, result.lost_percent)

def wait():
    print('Testing for %s seconds' % sys.argv[1])
    time.sleep(int(sys.argv[1]))
    print('==========================================================')
    print('Testing duration has finished, exiting program')
    print('==========================================================')
    os._exit(1)

def test():
    while 1 :
        test_tcp_upload()
        
background = threading.Thread(name = 'test_performance', target = test)
background.start()
wait()
