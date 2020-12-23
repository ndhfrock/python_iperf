#!/usr/bin/env python3

from ping3 import ping, verbose_ping
from tcp_latency import measure_latency
from mysql.connector import errorcode
from datetime import datetime
import mysql.connector
import iperf3
import sys
import time

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

    sql = "insert into test_performance values (CONVERT_TZ('%s-%s-%s %s:%s:%s','+08:00','+00:00'),%.3f,%.3f,%.3f,%.3f, %.3f)"
    #print(sql % (now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput_upload, latency, jitter, loss_rate))
    #print(now.strftime("%S"))
    mycursor.execute(sql % (now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput_upload, latency, jitter, loss_rate, throughput_download))

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

def test_tcp_upload():
    client = iperf3.Client()
    client.duration = 2
    client.server_hostname = '140.118.122.120'
    client.port = 5201
    #client.num_streams = 5
    #client.bandwidth = 1000000
    client.protocol = 'tcp'

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))
    
    # get test start time
    now = datetime.now()
    

    # Test the RTT first before iperf test
    rtt_list = measure_latency(host='140.118.122.120', port=3000, runs=1, timeout=2.5)

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

        test_tcp_download(result.sent_Mbps, rtt)

def test_tcp_download(throughput_upload, rtt):
    client = iperf3.Client()
    client.duration = 2
    client.server_hostname = '140.118.122.120'
    client.port = 5201
    #client.num_streams = 5
    #client.bandwidth = 1000000
    client.protocol = 'tcp'
    client.reverse = True

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

        test_udp(throughput_upload, result.sent_Mbps, rtt)

def test_udp(throughput_upload, throughput_download, rtt):
    client = iperf3.Client()
    client.duration = 2
    client.server_hostname = '140.118.122.120'
    client.port = 5201
    client.num_streams = 1
    client.bandwidth = 10000000
    client.bulksize = 1388
    client.protocol = 'udp'

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))

    # get test start time
    now = datetime.now()

    result = client.run()

    if result.error:
        print(result.error)
    else:
        test_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print('')
        print('Test completed:')
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

        mysql_insert(now, throughput_upload, throughput_download, rtt, result.jitter_ms, result.lost_percent)

i =  0
while i < int(sys.argv[1]):
    test_tcp_upload()
    time.sleep(1)
    i += 1