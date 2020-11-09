import iperf3

server = iperf3.Server()
server.bind_address = '140.118.122.120'
server.port = 6969
server.verbose = False
while True:
    server.run()