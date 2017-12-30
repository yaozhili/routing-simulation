from .transport import Transport
from .routing_table import RoutingTable
from .dispatcher import DataDispatcher
from .algorithm import DV, LS, CentralizedMember, CentralizedController
from .neighbors import Neighbors
from .config import Algorithm


class Router:

    def __init__(self, config):

        self._running = False

        self.routing_table = RoutingTable(config.hostname)
        self.dispatcher = DataDispatcher()

        self.neighbors = Neighbors(None, self.dispatcher)
        self.transport = Transport(
            config.hostname, config.self_addr.ip, config.self_addr.port,
            config.hns_addr.ip, config.hns_addr.port,
            self.routing_table, self.dispatcher, self.neighbors)
        self.neighbors.transport = self.transport

        self.algorithm = self.__get_algorithm(config)

    def __get_algorithm(self, config):
        if config.algorithm == Algorithm.LS_CENTRALIZE:
            return CentralizedMember(
                config.controller,
                config.hostname,
                self.transport,
                self.routing_table,
                self.neighbors,
                self.dispatcher,
                config.update_interval,
                config.dead_timeout)
        else:
            return {
                Algorithm.DV: DV,
                Algorithm.LS: LS,
                Algorithm.LS_CONTROL: CentralizedController}[
                config.algorithm](
                config.hostname,
                self.transport,
                self.routing_table,
                self.neighbors,
                self.dispatcher,
                config.update_interval,
                config.dead_timeout)

    def run(self):
        """
        start the router, if the router has already started, do nothing
        """
        if not self._running:
            self._running = True
            self.transport.run()
<<<<<<< HEAD
            self.algorithm.run()
=======
>>>>>>> c13ca62d259ff9265c3a398dab3411bddab18a9a

    def stop(self):
        """
        stop the working router, it no longer receiving or forwarding messages,
        if the router has stopped, do nothing
        """
        if self._running:
            self._running = False
            self.transport.stop()
<<<<<<< HEAD
            self.algorithm.stop()
=======
>>>>>>> c13ca62d259ff9265c3a398dab3411bddab18a9a

    def send(destination, message):
        """
        send message
        Args:
            destination(str): hostname for the receiver
            message(str): message to send
        """
        # data = {
        #     'type': ...
        #     'data': message
        # }
        # transport.send(destination, data)

    def get_alive(self):
        """
        get living hosts on this router's perspective
        Returns:
            list<str>: a list of the living hosts
        """
        self.routing_table.get_alive()

    def update_neighbor(self, name, cost):
        """
        add new neighbor to this router or update the cost of a neighbor
        """
        self.neighbors.update(name, cost)

    def remove_neighbor(self, name):
        """
        remove a neighbor with specified hostname
        """
        self.neighbors.remove(name)
