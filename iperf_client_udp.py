#!/usr/bin/env python3

from ping3 import ping, verbose_ping
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
import iperf3
import sys

def mysql_insert(now, throughput, latency, jitter, loss_rate):
    mydb = mysql.connector.connect(
        host="140.118.122.120",
        user="root",
        password="fihdan",
        database="test_grafana"
    )
    mycursor = mydb.cursor()

    sql = "insert into test_udp values (CONVERT_TZ('%s-%s-%s %s:%s:%s','+08:00','+00:00'),%.3f,%.3f,%.3f,%.3f)"
    #print(sql % (now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput, latency, jitter, loss_rate))
    #print(now.strftime("%S"))
    mycursor.execute(sql % (now.strftime("%Y"), now.strftime("%m"), now.strftime("%d"), now.strftime("%H"), now.strftime("%M"), now.strftime("%S"), throughput, latency, jitter, loss_rate))

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")

def test():
    client = iperf3.Client()
    client.duration = 1
    client.server_hostname = '140.118.122.120'
    client.port = 6969
    client.num_streams = 20
    client.bandwidth = 10000000
    client.bulksize = 8000
    client.protocol = 'udp'

    print('Connecting to {0}:{1}'.format(client.server_hostname, client.port))

    # get test start time
    now = datetime.now()

    #test the rtt using ping3 before iperf tcp testing
    rtt = None

    while rtt == None:
        rtt = ping('140.118.122.120', unit='ms')

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

        print('==========================================================')

        print("  Latency to target in ms is %.3f ms" %rtt)

        mysql_insert(now, result.Mbps, rtt, result.jitter_ms, result.lost_percent)

i =  0
while i < int(sys.argv[1]):
    test()
    i += 1