#!/usr/bin/env python3

from ping3 import ping, verbose_ping
from tcp_latency import measure_latency
from mysql.connector import errorcode
from datetime import datetime
import mysql.connector
import iperf3
import sys
import threading, time, os

test_number = 0
ip = sys.argv[3]

def test_tcp_upload():
    client = iperf3.Client()
    client.duration = 2
    client.server_hostname = ip
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
    
    result = client.run()

    if result.error:
        print(result.error)
    else:
        test_time = now.strftime("%d/%m/%Y %H:%M:%S")
        print('')
        print('Test completed for Upload:')
        print("  started at                 ",test_time)	
        #print('  started at                  {0}'.format(result.time))	
        #print('  started at (second)         {0}'.format(result.timesecs))
        #print('  bits transmitted           {0}'.format(result.sent_Mbps))
        #print('  bits received              {0}'.format(result.received_Mbps))
        #print('  loss packet                {0}'.format(result.lost_packets))
        #print('  loss packet percentage    {0}'.format(result.lost_percent))
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

        mysql_insert_upload(now, result.sent_Mbps)

def mysql_insert_upload(now, throughput_upload):
    mydb = mysql.connector.connect(
        host="172.17.0.3",
        user="root",
        password="yourpassword",
        database="iperf3_testing",
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()

    sql = "insert into test_performance_%s (time, throughput_upload) values (CONVERT_TZ('%s-%s-%s %s:%s:%s','+08:00','+00:00'),%.3f)"
    mycursor.execute(sql % (sys.argv[2], now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput_upload))

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

def test_tcp_download():
    client = iperf3.Client()
    client.duration = 2
    client.server_hostname = ip
    client.port = 5201
    client.num_streams = 15
    client.protocol = 'tcp'
    client.reverse = True
    client.omit = 1

    print('==========================================================')
    print('Test number %d' %test_number)
    print('==========================================================')

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
        #print('  started at                  {0}'.format(result.time))	
        #print('  started at (second)         {0}'.format(result.timesecs))
        #print('  bits transmitted           {0}'.format(result.sent_Mbps))
        #print('  bits received              {0}'.format(result.received_Mbps))
        #print('  loss packet                {0}'.format(result.lost_packets))
        #print('  loss packet percentage    {0}'.format(result.lost_percent))
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

        mysql_insert_download(now, result.sent_Mbps)

def mysql_insert_download(now, throughput_download):
    mydb = mysql.connector.connect(
        host="172.17.0.3",
        user="root",
        password="yourpassword",
        database="iperf3_testing",
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()

    sql = "insert into test_performance_%s (time, throughput_download) values (CONVERT_TZ('%s-%s-%s %s:%s:%s','+08:00','+00:00'),%.3f)"
    mycursor.execute(sql % (sys.argv[2], now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput_download))

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")


def listToString(s):  
    
    # initialize an empty string 
    str1 = 0
    
    # traverse in the string   
    for ele in s:  
        str1 += ele   
    
    # return string   
    return str1  

def test_tcp_latency():
    client = iperf3.Client()
    client.server_hostname = ip
    client.protocol = 'tcp'

    print('==========================================================')
    print('Test number %d' %test_number)
    print('==========================================================')
    
    # get test start time
    now = datetime.now()

    # Test the RTT
    rtt_list = measure_latency(host=ip, port=client.port, runs=1, timeout=2.5)

    while rtt_list[0] == None:
        rtt_list = measure_latency(host=ip, port=client.port, runs=1, timeout=2.5)

    #change from list to float
    rtt = float(rtt_list[0])

    test_time = now.strftime("%d/%m/%Y %H:%M:%S")

    print('')
    print('Test completed for Latency:')
    print("  started at                 ",test_time)	

    print('==========================================================')

    print("  Latency to target in ms is %.3f ms" %rtt)

    print('==========================================================')

    mysql_insert_latency(now, rtt)

def mysql_insert_latency(now, latency):
    mydb = mysql.connector.connect(
        host="172.17.0.3",
        user="root",
        password="yourpassword",
        database="iperf3_testing",
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()

    sql = "insert into test_performance_%s (time, latency) values (CONVERT_TZ('%s-%s-%s %s:%s:%s','+08:00','+00:00'),%.3f)"
    mycursor.execute(sql % (sys.argv[2], now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), latency))

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

def test_udp():
    client = iperf3.Client()
    client.duration = 2
    client.server_hostname = ip
    client.port = 5201
    client.num_streams = 1
    client.bandwidth = 10000000
    client.bulksize = 1470
    client.protocol = 'udp'
    client.omit = 1

    print('==========================================================')
    print('Test number %d' %test_number)
    print('==========================================================')

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
        #print('  started at                 {0}'.format(result.time))	
        #print('  started at (second)        {0}'.format(result.timesecs))

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

        mysql_insert_udp(now, result.jitter_ms, result.lost_percent)

def mysql_insert_udp(now, jitter, loss_rate):
    mydb = mysql.connector.connect(
        host="172.17.0.3",
        user="root",
        password="yourpassword",
        database="iperf3_testing",
        auth_plugin='mysql_native_password'
    )
    mycursor = mydb.cursor()

    sql = "insert into test_performance_%s (time, jitter, loss_rate) values (CONVERT_TZ('%s-%s-%s %s:%s:%s','+08:00','+00:00'),%.3f, %.3f)"
    mycursor.execute(sql % (sys.argv[2], now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), jitter, loss_rate))

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

def test():
    print('Testing for %s times' % sys.argv[1])
    test_number = 0
    while test_number < int(sys.argv[1]) :
        test_tcp_upload()
        test_number += 1
    test_number = 0
    while test_number < int(sys.argv[1]) :
        test_tcp_download()
        test_number += 1
    test_number = 0
    while test_number < int(sys.argv[1]) :
        test_tcp_latency()
        test_number += 1
    test_number = 0
    while test_number < int(sys.argv[1]) :
        test_udp()
        test_number += 1

test()