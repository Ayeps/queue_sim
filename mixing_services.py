#!/usr/bin/python3

from netsimutils import *
import numpy as np
import matplotlib.pyplot as plt
import random


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 1234
INTER_ARRIVAL = 2.0
SERVICE_TIME = 16.0
NUM_MACHINES = 4
QUEUE_SIZE = 50

SIM_TIME = 100000

# one arival process for each queue with reduced arrival rate.
def mixed_queues():
    # ********************************
    # setup and perform the simulation
    # ********************************

    #env = simpy.Environment()


    servers = []
    arrivals = []
    env = simpy.Environment()
    # create a fast server
    packet_arrival = PacketArrival(env, INTER_ARRIVAL*2)
    server_farm = Service(env, 1, SERVICE_TIME/NUM_MACHINES, QUEUE_SIZE)
    arrivals.append(packet_arrival)
    servers.append(server_farm)
    env.process(packet_arrival.arrival_process(server_farm))
    #create NUM_MACHINES slow servers
    for i in range(NUM_MACHINES):
        packet_arrival = PacketArrival(env, INTER_ARRIVAL*2*NUM_MACHINES)
        server_farm = Service(env, 1, SERVICE_TIME, QUEUE_SIZE)
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

class PacketArrivalMod(PacketArrival):
    """Documentation for PacketArrivalMod

    """
    def __init__(self, envi, int_arriv_time):
        super(PacketArrivalMod, self).__init__(envi, int_arriv_time)
        return
    def arrival_process(self, servers, probabilities):
        distribution=[]
        for i, p in zip(range(0,len(servers)), probabilities):
            self.ia_times.append([])
            while p > 0:
                distribution.append(i)
                p-=1
        while True:
            i = distribution[int(random.uniform(0, len(distribution)))]
            j = (i+len(servers)-1) % len(servers)

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)

            # a car has arrived - request carwash to do its job
            while i==j and servers[i].qsize == servers[i].qsize_limit:
                i = (i+1) % len(servers)
            self.ia_times[i].append(inter_arrival)
            self.env.process(servers[i].service())

# one arival process. Avoid to put a process on a full queue
def mixed_queues_losses_avoidance():
    # ********************************
    # setup and perform the simulation
    # ********************************

    #env = simpy.Environment()


    servers = []
    probs = []
    env = simpy.Environment()
    # create a fast server
    server_farm = Service(env, 1, SERVICE_TIME/NUM_MACHINES, QUEUE_SIZE, SIM_TIME)
    probs.append(NUM_MACHINES)
    servers.append(server_farm)
    #create NUM_MACHINES slow servers
    for i in range(NUM_MACHINES):
        server_farm = Service(env, 1, SERVICE_TIME, QUEUE_SIZE, SIM_TIME)
        servers.append(server_farm)
        probs.append(1)

    p = PacketArrivalMod(env, INTER_ARRIVAL)
    env.process(p.arrival_process(servers, probs))
    # simulate until SIM_TIME
    print("Running simulation")
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
    for i, ia_times in enumerate(p.ia_times):
        tot = len(ia_times)
        supertot += tot
        superlost += servers[i].lost
        super_ia_times.append(ia_times)
        print(repr(tot) + " total packets for queue n." + repr(i))
        print(repr(servers[i].lost) + " packets lost for queue n." + repr(i) +
              "(" + repr(servers[i].lost/tot * 100) + "%)")    
        #plot
        print("First plot")
        fig, (series, pdf, cdf) = plt.subplots(3, 1)
        fig.title = "server "+ repr(i)
        
        series.plot(ia_times)
        series.set_xlabel("Sample")
        series.set_ylabel("Inter-arrival")

        pdf.hist(ia_times, bins=100, normed=True)
        pdf.set_xlabel("Time")
        pdf.set_ylabel("Density")
        pdf.set_xbound(0, 15)

        cdf.hist(ia_times, bins=100, cumulative=True, normed=True)
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



def main():
    random.seed(RANDOM_SEED)
    #mixed_queues()
    mixed_queues_losses_avoidance()
    plt.show()

if __name__ == '__main__':
    main()
