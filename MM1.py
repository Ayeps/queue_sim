#!/usr/bin/python3
import numpy as np
import simpy
import random
import matplotlib.pyplot as plt


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
INTER_ARRIVAL = 2.0
SERVICE_TIME = 8.0
NUM_MACHINES = 4
QUEUE_SIZE = 50

SIM_TIME = 100000

# **********************************************************************************************************************
# Packet arrival
# **********************************************************************************************************************
#
class PacketArrival(object):
    """ Questa classe genera soltanto l'arrivo dei processi
"""
    # constructor
    def __init__(self, environ, arrival_time):

        # the inter-arrival time
        self.arrival_time = arrival_time

        # the environment
        self.env = environ

        self.ia_times = []
        # execute the process
    def arrival_process(self, server_farm):
        while True:
            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)
            self.ia_times.append(inter_arrival)

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)

            # a car has arrived - request carwash to do its job
            self.env.process(server_farm.service())


# **********************************************************************************************************************
# Packet Processing - it gets a waiting process (FCFS) and performs the service
# **********************************************************************************************************************
class Service(object):
    """Questo mette in coda o scarta i pacchetti e serve le richieste
(Segue il pacchetto dall'inserimento in coda fino alla fine del servizio)

    """
    def __init__(self, environment, n_servers, s_time):
        self.environment = environment
        self.servers = simpy.Resource(environment, n_servers)
        self.s_time = s_time
        self.qsize = 0
        self.lost = 0
        self.re_times = []

        
    def service(self):
        #print("Packets in queue: %d" % self.qsize)
        if self.qsize == QUEUE_SIZE:
            #print("Packet lost at %f" % env.now )
            self.lost += 1
        else:
            self.qsize += 1
            t0 = self.environment.now
            #print("Packet arrived in queue at %f" % env.now)
            with self.servers.request() as req:
                yield req

                service_time = random.expovariate(1.0/self.s_time)
                yield self.environment.timeout(service_time)
                #print("Packet left the server at %f" % env.now)
                t1 = self.environment.now
                self.re_times.append(t1-t0)
                self.qsize -= 1


def n_independent_queues():
    # ********************************
    # setup and perform the simulation
    # ********************************

    env = simpy.Environment()


    servers = []
    arrivals = []
    for _ in range(NUM_MACHINES):
        packet_arrival = PacketArrival(env, INTER_ARRIVAL*NUM_MACHINES)
        server_farm = Service(env, 1, SERVICE_TIME)
        arrivals.append(packet_arrival)
        servers.append(server_farm)

        # start the arrival process
        env.process(packet_arrival.arrival_process(server_farm))

    # simulate until SIM_TIME
    env.run(SIM_TIME)

    #compute the average
    m = 0
    for s in servers:
       m += np.mean(s.re_times)
    m /= NUM_MACHINES
    print("mean response time = " + repr(m))


    supertot = 0
    superlost = 0
    super_ia_times = []
    for i, packet_arrival in enumerate(arrivals):
        tot = len(packet_arrival.ia_times)
        supertot += tot
        superlost += server_farm.lost
        super_ia_times.append(packet_arrival.ia_times)
        print(repr(tot) + " total packets for queue n." + repr(i))
        print(repr(server_farm.lost) + " packets lost for queue n." + repr(i) +
              "(" + repr(server_farm.lost/tot * 100) + "%)")    
        #plot
        fig, (series, pdf, cdf) = plt.subplots(3, 1)
        fig.title = "server "+ repr(i)
        
        series.plot(packet_arrival.ia_times)
        series.set_xlabel("Sample")
        series.set_ylabel("Inter-arrival")

        pdf.hist(packet_arrival.ia_times, bins=100, normed=True)
        pdf.set_xlabel("Time")
        pdf.set_ylabel("Density")
        pdf.set_xbound(0, 15)

        cdf.hist(packet_arrival.ia_times, bins=100, cumulative=True, normed=True)
        cdf.set_xlabel("Time")
        cdf.set_ylabel("P(Arrival time <= x)")
        cdf.set_ybound(0, 1)
        cdf.set_xbound(0, 15)
        
    print(repr(supertot) + " total packets")
    print(repr(superlost) + " packets lost (" + repr(superlost/supertot * 100) + "%)")    

    #plot
    fig, (pdf, cdf) = plt.subplots(2, 1)

    pdf.hist(super_ia_times, bins=100, normed=True)
    pdf.set_xlabel("Time")
    pdf.set_ylabel("Density")
    pdf.set_xbound(0, 15)

    cdf.hist(super_ia_times, bins=100, cumulative=True, normed=True)
    cdf.set_xlabel("Time")
    cdf.set_ylabel("P(Arrival time <= x)")
    cdf.set_ybound(0, 1)
    cdf.set_xbound(0, 15)

    
def n_services():
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
    env.run(SIM_TIME)

    #compute the average
    m = np.mean(server_farm.re_times)
    print("mean response time = " + repr(m))

    tot = len(packet_arrival.ia_times)
    print(repr(tot) + " total packets")
    print(repr(server_farm.lost) + " packets lost (" + repr(server_farm.lost/tot * 100) + "%)")    
    #plot
    fig, (series, pdf, cdf) = plt.subplots(3, 1)

    series.plot(packet_arrival.ia_times)
    series.set_xlabel("Sample")
    series.set_ylabel("Inter-arrival")

    pdf.hist(packet_arrival.ia_times, bins=100, normed=True)
    pdf.set_xlabel("Time")
    pdf.set_ylabel("Density")
    pdf.set_xbound(0, 15)

    cdf.hist(packet_arrival.ia_times, bins=100, cumulative=True, normed=True)
    cdf.set_xlabel("Time")
    cdf.set_ylabel("P(Arrival time <= x)")
    cdf.set_ybound(0, 1)
    cdf.set_xbound(0, 15)


def fast_service():
    # ********************************
    # setup and perform the simulation
    # ********************************

    env = simpy.Environment()

    # car arrival
    packet_arrival = PacketArrival(env, INTER_ARRIVAL)

    # carwash
    server_farm = Service(env, 1, SERVICE_TIME/NUM_MACHINES)

    # start the arrival process
    env.process(packet_arrival.arrival_process(server_farm))

    # simulate until SIM_TIME
    env.run(SIM_TIME)

    #compute the average
    m = np.mean(server_farm.re_times)
    print("mean response time = " + repr(m))

    tot = len(packet_arrival.ia_times)
    print(repr(tot) + " total packets")
    print(repr(server_farm.lost) + " packets lost (" + repr(server_farm.lost/tot * 100) + "%)")    
    #plot
    fig, (series, pdf, cdf) = plt.subplots(3, 1)

    series.plot(packet_arrival.ia_times)
    series.set_xlabel("Sample")
    series.set_ylabel("Inter-arrival")

    pdf.hist(packet_arrival.ia_times, bins=100, normed=True)
    pdf.set_xlabel("Time")
    pdf.set_ylabel("Density")
    pdf.set_xbound(0, 15)

    cdf.hist(packet_arrival.ia_times, bins=100, cumulative=True, normed=True)
    cdf.set_xlabel("Time")
    cdf.set_ylabel("P(Arrival time <= x)")
    cdf.set_ybound(0, 1)
    cdf.set_xbound(0, 15)

    
    


# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    n_services()
    n_independent_queues()
    fast_service()

    plt.show()
