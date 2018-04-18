import simpy
import random
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
    def __init__(self, environment, n_servers, s_time, QUEUE_SIZE):
        self.environment = environment
        self.servers = simpy.Resource(environment, n_servers)
        self.s_time = s_time
        self.qsize = 0
        self.lost = 0
        self.re_times = []
        self.qsize_limit = QUEUE_SIZE

        
    def service(self):
        #print("Packets in queue: %d" % self.qsize)
        if self.qsize == self.qsize_limit:
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
