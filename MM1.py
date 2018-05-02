#!/usr/bin/python3
import numpy as np
import simpy
import random
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from netsimutils import *
from scipy.interpolate import spline


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************

RANDOM_SEED = 45
INTER_ARRIVAL = 2
SERVICE_TIME = 9
NUM_MACHINES = 4
QUEUE_SIZE = 50

SIM_TIME = 10000

def n_independent_queues():
    # ********************************
    # setup and perform the simulation
    # ********************************

    #env = simpy.Environment()

    servers = []
    arrivals = []
    for _ in range(NUM_MACHINES):
        env = simpy.Environment()
        packet_arrival = PacketArrival(env, NUM_MACHINES*INTER_ARRIVAL )
        server_farm = Service(env, 1, SERVICE_TIME, QUEUE_SIZE, SIM_TIME)
        arrivals.append(packet_arrival)
        servers.append(server_farm)

        # start the arrival process
        env.process(packet_arrival.arrival_process(server_farm))

        # simulate until SIM_TIME
        env.run(SIM_TIME)
        print("mean response time = " + repr(np.mean(server_farm.re_times)))

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
        # # plot
        # plt.subplot(311)
        # plt.plot(packet_arrival.ia_times)
        # plt.xlabel("Sample")
        # plt.ylabel("Inter-arrival")
        #
        # plt.subplot(312)
        # plt.hist(packet_arrival.ia_times, bins=100, normed=True)
        # plt.xlabel("Time")
        # plt.ylabel("Density")
        #
        # plt.subplot(313)
        # plt.hist(packet_arrival.ia_times, bins=100, cumulative=True, normed=True)
        # plt.xlabel("Time")
        # plt.ylabel("P(Arrival time <= x)")
        #
        # plt.suptitle("server " + repr(i))
        # plt.subplots_adjust(hspace=0.6)
        # plt.show()

    super_dynamic_QS = []
    super_lost_s = []
    for i in range(len(servers)):
        super_dynamic_QS.append(servers[i].dynamic_QS)
        super_lost_s.append(servers[i].lost_s)
        
    print(repr(supertot) + " total packets")
    print(repr(superlost) + " packets lost (" + repr(superlost/supertot * 100) + "%)")    

    ################
    # PLOT SECTION #
    ################
    plt.subplot(3, 4, 1)
    plt.plot(super_ia_times[0])
    plt.subplot(3, 4, 2)
    plt.plot(super_ia_times[1])
    plt.subplot(3, 4, 3)
    plt.plot(super_ia_times[2])
    plt.subplot(3, 4, 4)
    plt.plot(super_ia_times[3])

    plt.subplot(3,4,5)
    plt.hist(super_ia_times[0], bins=100, normed=True)
    plt.subplot(3,4,6)
    plt.hist(super_ia_times[1], bins=100, normed=True)
    plt.subplot(3,4,7)
    plt.hist(super_ia_times[2], bins=100, normed=True)
    plt.subplot(3,4,8)
    plt.hist(super_ia_times[3], bins=100, normed=True)

    plt.subplot(3, 4, 9)
    plt.hist(super_ia_times[0], bins=100, cumulative=True, normed=True)
    plt.subplot(3, 4, 10)
    plt.hist(super_ia_times[1], bins=100, cumulative=True, normed=True)
    plt.subplot(3, 4, 11)
    plt.hist(super_ia_times[2], bins=100, cumulative=True, normed=True)
    plt.subplot(3, 4, 12)
    plt.hist(super_ia_times[3], bins=100, cumulative=True, normed=True)
    plt.show()


    ax=plt.subplot(4,2,1)
    plt.plot(super_dynamic_QS[0])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x*2)))
    plt.ylabel("Packets in queue")
    plt.title("Queue Size")

    ax = plt.subplot(4,2,2)
    plt.plot(super_lost_s[0])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y / 50)))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * 50)))
    plt.title("Losses")
    plt.ylabel("Packets lost")
    plt.xlabel("Time")

    ax=plt.subplot(4,2,3)
    plt.plot(super_dynamic_QS[1])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x*2)))
    plt.ylabel("Packets in queue")
    plt.title("Queue Size")

    ax = plt.subplot(4,2,4)
    plt.plot(super_lost_s[1])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y / 50)))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * 50)))
    plt.title("Losses")
    plt.ylabel("Packets lost")
    plt.xlabel("Time")

    ax=plt.subplot(4,2,5)
    plt.plot(super_dynamic_QS[2])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x*2)))
    plt.ylabel("Packets in queue")
    plt.title("Queue Size")

    ax = plt.subplot(4,2,6)
    plt.plot(super_lost_s[2])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y / 50)))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * 50)))
    plt.title("Losses")
    plt.ylabel("Packets lost")
    plt.xlabel("Time")

    ax=plt.subplot(4,2,7)
    plt.plot(super_dynamic_QS[3])
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x*2)))
    plt.ylabel("Packets in queue")
    plt.title("Queue Size")

    ax = plt.subplot(4,2,8)
    plt.plot(super_lost_s[3])
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y / 50)))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * 50)))
    plt.title("Losses")
    plt.ylabel("Packets lost")
    plt.xlabel("Time")

    plt.subplots_adjust(hspace=0.6)
    plt.suptitle('N Services')
    plt.show()

    
def n_services():
    # ********************************
    # setup and perform the simulation
    # ********************************

    env = simpy.Environment()

    # car arrival
    packet_arrival = PacketArrival(env, INTER_ARRIVAL)

    # carwash
    server_farm = Service(env, NUM_MACHINES, SERVICE_TIME, QUEUE_SIZE, SIM_TIME)

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

    ################
    # PLOT SECTION #
    ################

    plt.subplot(311)
    plt.plot(packet_arrival.ia_times)
    plt.xlabel("Sample")
    plt.ylabel("Inter-arrival")

    plt.subplot(312)
    plt.hist(packet_arrival.ia_times, bins=100, normed=True)
    plt.xlabel("Time")
    plt.ylabel("Density")

    plt.subplot(313)
    plt.hist(packet_arrival.ia_times, bins=100, cumulative=True, normed=True)
    plt.xlabel("Time")
    plt.ylabel("P(Arrival time <= x)")

    plt.subplots_adjust(hspace=0.6)
    plt.suptitle('N Services')
    plt.show()

    # PLOT LOSSES

    ax=plt.subplot(211)
    plt.plot(server_farm.dynamic_QS)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x*2)))
    plt.ylabel("Packets in queue")
    plt.title("Queue Size")

    ax = plt.subplot(212)
    plt.plot(server_farm.lost_s)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y / 50)))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * 50)))
    plt.title("Losses")
    plt.ylabel("Packets lost")
    plt.xlabel("Time")

    plt.subplots_adjust(hspace=0.6)
    plt.suptitle('N Services')
    plt.show()

def fast_service():
    # ********************************
    # setup and perform the simulation
    # ********************************

    env = simpy.Environment()

    # car arrival
    packet_arrival = PacketArrival(env, INTER_ARRIVAL)

    # carwash
    server_farm = Service(env, 1, SERVICE_TIME/NUM_MACHINES, QUEUE_SIZE, SIM_TIME)

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

    ################
    # PLOT SECTION #
    ################

    plt.subplot(311)
    plt.plot(packet_arrival.ia_times)
    plt.xlabel("Sample")
    plt.ylabel("Inter-arrival")

    plt.subplot(312)
    plt.hist(packet_arrival.ia_times, bins=100, normed=True)
    plt.xlabel("Time")
    plt.ylabel("Density")

    plt.subplot(313)
    plt.hist(packet_arrival.ia_times, bins=100, cumulative=True, normed=True)
    plt.xlabel("Time")
    plt.ylabel("P(Arrival time <= x)")

    plt.subplots_adjust(hspace=0.6)

    plt.suptitle('Fast Serivce')
    plt.show()

    # PLOT LOSSES

    ax=plt.subplot(211)
    plt.plot(server_farm.dynamic_QS)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x*2)))
    plt.ylabel("Packets in queue")
    plt.title("Queue Size")

    ax = plt.subplot(212)
    plt.plot(server_farm.lost_s)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: ('%g') % (y / 50)))
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: ('%g') % (x * 50)))
    plt.title("Losses")
    plt.ylabel("Packets lost")
    plt.xlabel("Time")

    plt.subplots_adjust(hspace=0.6)
    plt.suptitle('Fast Service')
    plt.show()
    
    


# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    print()
    print("M/M/n")
    n_services()
    print()
    print("n x M/M/1")
    n_independent_queues()
    print()
    print("M/M/1 high speed")
    fast_service()
