#!/usr/bin/python3

import simpy
import random
import matplotlib.pyplot as plt


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
INTER_ARRIVAL = 2.0
SERVICE_TIME = 16.0
NUM_MACHINES = 4
QUEUE_SIZE = 50

SIM_TIME = 100000

# **********************************************************************************************************************
# Packet arrival
# **********************************************************************************************************************
class PacketArrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        # the inter-arrival time
        self.arrival_time = arrival_time

        # the environment
        self.env = environ

        self.times = []


        # execute the process
    def arrival_process(self, server_farm):
        while True:
            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)
            self.times.append(inter_arrival)

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)

            # a car has arrived - request carwash to do its job
            self.env.process(server_farm.service())


# **********************************************************************************************************************
# Packet Processing - it gets a waiting process (FCFS) and performs the service
# **********************************************************************************************************************
class Service(object):
    """Documentation for Service

    """
    def __init__(self, environment, n_servers, s_time):
        self.environment = environment
        self.servers = simpy.Resource(environment, n_servers)
        self.s_time = s_time
        self.qsize = 0
        self.lost = 0
        
    def service(self):
        print("Packets in queue: %d" % self.qsize)
        if self.qsize == QUEUE_SIZE:
            print("Packet lost at %f" % env.now )
            self.lost += 1
        else:
            self.qsize += 1
            print("Packet arrived in queue at %f" % env.now)
            with self.servers.request() as req:
                yield req

                service_time = random.expovariate(1.0/self.s_time)
                yield self.environment.timeout(service_time)
                print("Packet left the server at %f" % env.now)
                self.qsize -= 1
        



# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    # ********************************
    # setup and perform the simulation
    # ********************************

    env = simpy.Environment()

    # car arrival
    packet_arrival = PacketArrival(env, INTER_ARRIVAL)

    # carwash
    server_farm = Service(env, NUM_MACHINES, SERVICE_TIME)

    # start the arrival process
    env.process(packet_arrival.arrival_process(server_farm))

    # simulate until SIM_TIME
    env.run(until=SIM_TIME)

    fig, (series, pdf, cdf) = plt.subplots(3, 1)

    series.plot(packet_arrival.times)
    series.set_xlabel("Sample")
    series.set_ylabel("Inter-arrival")

    pdf.hist(packet_arrival.times, bins=100, normed=True)
    pdf.set_xlabel("Time")
    pdf.set_ylabel("Density")
    pdf.set_xbound(0, 15)

    cdf.hist(packet_arrival.times, bins=100, cumulative=True, normed=True)
    cdf.set_xlabel("Time")
    cdf.set_ylabel("P(Arrival time <= x)")
    cdf.set_ybound(0, 1)
    cdf.set_xbound(0, 15)

    plt.show()
