#!/usr/bin/python3
from typing import TextIO

import numpy as np
import simpy
import random
import matplotlib.pyplot as plt
from netsimutils import *


# **********************************************************************************************************************
# Constants
# **********************************************************************************************************************
RANDOM_SEED = 42
INTER_ARRIVAL = 2.0
SERVICE_TIME = 8.0
NUM_MACHINES = 4
QUEUE_SIZE = 50

SIM_TIME = 1000


def n_independent_queues(fileName):
    # ********************************
    # setup and perform the simulation
    # ********************************


    with open(fileName, mode="w") as filePointer:  # type: TextIO


        env = simpy.Environment()

    servers = []
    arrivals = []
    for _ in range(NUM_MACHINES):
        env = simpy.Environment()
        packet_arrival = PacketArrival(env, NUM_MACHINES*INTER_ARRIVAL )
        server_farm = Service(env, 1, SERVICE_TIME, QUEUE_SIZE)
        arrivals.append(packet_arrival)
        servers.append(server_farm)

        servers = []
        arrivals = []
        for _ in range(NUM_MACHINES):
            packet_arrival = PacketArrival(env, INTER_ARRIVAL*NUM_MACHINES)
            server_farm = Service(env, 1, SERVICE_TIME, filePointer)
            arrivals.append(packet_arrival)
            servers.append(server_farm)

        # simulate until SIM_TIME
        env.run(SIM_TIME)

   ##compute the average
   #m = 0
   #for s in servers:
   #   m += np.mean(s.re_times)
   #m /= NUM_MACHINES
        print("mean response time = " + repr(np.mean(server_farm.re_times)))

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

            plt.suptitle("server " + repr(i))
            plt.subplots_adjust(hspace=0.6)
            plt.show(block=False)


        print(repr(supertot) + " total packets")
        print(repr(superlost) + " packets lost (" + repr(superlost/supertot * 100) + "%)")

        #plot
        plt.subplot(211)
        plt.hist(super_ia_times, bins=100, normed=True)
        plt.xlabel("Time")
        plt.ylabel("Density")

        plt.subplot(212)
        plt.hist(super_ia_times, bins=100, cumulative=True, normed=True)
        plt.xlabel("Time")
        plt.ylabel("P(Arrival time <= x)")
        plt.show(block=False)

    
def n_services(fileName):
    # ********************************
    # setup and perform the simulation
    # ********************************
    with open(fileName, mode="w") as filePointer:  # type: TextIO

        env = simpy.Environment()

        # car arrival
        packet_arrival = PacketArrival(env, INTER_ARRIVAL)

        # carwash
        server_farm = Service(env, NUM_MACHINES, SERVICE_TIME, QUEUE_SIZE)


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
        plt.show(block=False)


def fast_service(fileName):
    # ********************************
    # setup and perform the simulation
    # ********************************

    with open(fileName, mode="w") as filePointer:  # type: TextIO

        env = simpy.Environment()

        # car arrival
        packet_arrival = PacketArrival(env, INTER_ARRIVAL)


        # carwash
        server_farm = Service(env, 1, SERVICE_TIME/NUM_MACHINES, QUEUE_SIZE)


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

        plt.suptitle('Fast service')
        plt.show()



    
    


# **********************************************************************************************************************
# the "main" of the simulation
# **********************************************************************************************************************
if __name__ == '__main__':

    random.seed(RANDOM_SEED)
    n_services("n_services.txt")
    n_independent_queues("n_independent_queues.txt")
    fast_service("fast_service.txt")
