# -*- coding: utf-8 -*-

##
# @author G. Gbikpi-Benissan, MRG, CentraleSupelec, France
# @date 2016-02-08, 2016-02-18
# @version 1.0
#
# @class NetSim
#

# -- Third-party modules
import numpy

##
# @brief An interactive tool for network simulation.
#
class NetSim ( object ) :

  # ----------------------------------------------------------------------------
  # -- CLASS ATTRIBUTES
  # ----------------------------------------------------------------------------

  # Error status
  SUCCESS = 0
  FAILURE = 1

  # Network node state
  ST_WORK = 0
  ST_COMM = 1

  # Class description
  CLASS_NAME = "NetSim"
  CLASS_AUTHOR = "G. G.-Benissan, MRG, CentraleSupelec, France"
  METHODS = """
  __init__ (
        self,
        numb_node,
        numb_link,
        node2link,
        node2node,
        p_node2node,
        node_size = numpy.array([]),
        link_size = numpy.array([]),
        numb_iter = 1 )

  Step ( self )
  """

  # ----------------------------------------------------------------------------
  # -- INITIALIZATION
  # ----------------------------------------------------------------------------

  ##
  # @param numb_node = number of network nodes
  # @param numb_link = number of communication links
  #
  # @param node2link = communication links of each node (CSR data)
  # @param node2node = corresponding neighbor nodes (CSR column indices)
  # @param p_node2node = index of each node (CSR row pointer)
  #             (numpy.ndarray, numpy.ndarray, numpy.ndarray)
  #
  # @param node_size = workload on each node
  #             [default: numpy.array([20]*numb_node, dtype=int)]
  # @param link_size = transfer size on each link
  #             [default: numpy.array([20]*numb_link, dtype=int)]
  # @param numb_iter = number of iterations
  #             [default: 1]
  # @remarks There is not any copy of the input arrays.
  #
  def __init__ (
        self,
        numb_node,
        numb_link,
        node2link,
        node2node,
        p_node2node,
        node_size = numpy.array([]),
        link_size = numpy.array([]),
        numb_iter = 1 ) :

    # -- Topology
    self.numb_node = numb_node
    self.numb_link = numb_link
    self.node2link = node2link
    self.node2node = node2node
    self.p_node2node = p_node2node

    # -- Features

    # Node size
    if (len(node_size) > 0) :
      self.node_size = node_size
    else :
      self.node_size = 20 + numpy.zeros(self.numb_node, dtype=int)

    # Link size
    if (len(link_size) > 0) :
      self.link_size = 2 * link_size
    else :
      self.link_size = 20 + numpy.zeros(self.numb_link, dtype=int)

    # -- Simulation

    # Parameters
    self.numb_iter = numb_iter + numpy.zeros(self.numb_node, dtype=int)

    # State
    self.glob_iter = 0
    self.node_iter = numpy.zeros(self.numb_node, dtype=int)
    self.node_conn = self.p_node2node[0:self.numb_node].copy()
    self.node_state = NetSim.ST_WORK + numpy.zeros(self.numb_node, dtype=int)
    self.__Step = [self.StepNodeLocal] * self.numb_node

    # Output
    self.node_step = numpy.zeros(self.numb_node, dtype=int)
    self.link_step = numpy.zeros(self.numb_link, dtype=int)
    self.flag_end = False
    self.numb_step = numpy.zeros(min(self.numb_iter), dtype=int)

    # -- Error handling

    # Last error code
    self.err_code = NetSim.SUCCESS

    # Last error message
    self.err_msg = ""

  # END def __init__ (
#        self,
#        numb_node,
#        numb_link,
#        node2link,
#        node2node,
#        p_node2node,
#        node_size = numpy.array([]),
#        link_size = numpy.array([]),
#        numb_iter = 1 ) :
  # ----------------------------------------------------------------------------

  # ----------------------------------------------------------------------------
  # -- PROCESS
  # ----------------------------------------------------------------------------

  ##
  # @brief Performs one atomic simulation step.
  #
  def Step ( self ) :

    # -- init

    # error handling
    self.err_code = NetSim.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + NetSim.CLASS_NAME + ".Step]"

    # -- step
    for i in range(0, self.numb_node) :
      if (self.node_iter[i] < self.numb_iter[i]) :
        self.__Step[i](i)
        if (self.err_code == NetSim.FAILURE) :
          self.err_msg = err_header + "\n" + self.err_msg
          return

    # -- update output
    self.numb_step[self.glob_iter] += 1
    if (self.glob_iter not in self.node_iter) :
      self.glob_iter += 1
    self.flag_end = (False not in (self.node_iter == self.numb_iter))

    return

  # END def Step ( self ) :
  # ----------------------------------------------------------------------------

  ##
  # @brief Performs one atomic local step of a given node.
  # @param node = node number
  #
  def StepNodeLocal (
        self,
        node ) :

    # -- step
    self.node_step[node] += 1

    # -- update state
    if (self.node_step[node] == self.node_size[node]) :
      self.node_step[node] = 0
      self.node_state[node] = NetSim.ST_COMM
      self.__Step[node] = self.StepNodeConnect
      print("[{:s}] [{:d}] {:4d}  -->|  {:d}".format(NetSim.CLASS_NAME,
              self.node_iter[node], node, self.node2node[self.node_conn[node]]))


    return

  # END def StepNodeLocal (
#        self,
#        node ) :
  # ----------------------------------------------------------------------------

  ##
  # @brief Performs one connection attempt for a given node.
  # @param node = node number
  #
  def StepNodeConnect (
        self,
        node ) :

    # -- init

    # error handling
    self.err_code = NetSim.SUCCESS
    self.err_msg = ""

    # -- get targeted neighbor node
    neighb = self.node2node[self.node_conn[node]]

    # -- attempt connection
    neighb_conn = self.node_conn[neighb]
    if ((node == self.node2node[neighb_conn])
        and (self.node_state[neighb] == NetSim.ST_COMM)) :
      self.__Step[node] = self.StepNodeTransfer
      print("[{:s}] [{:d}] {:4d}  <-->  {:d}".format(NetSim.CLASS_NAME,
            self.node_iter[node], node, neighb))


    return

  # END def StepNodeConnect (
#        self,
#        node ) :
  # ----------------------------------------------------------------------------

  ##
  # @brief Performs one atomic data transfer step of a given node.
  # @param node = node number
  #
  def StepNodeTransfer (
        self,
        node ) :

    # -- init

    # error handling
    self.err_code = NetSim.SUCCESS
    self.err_msg = ""

    # -- get link
    link = self.node2link[self.node_conn[node]]

    # -- step
    self.link_step[link] += 1

    # -- update state
    if (self.link_step[link] >= (self.link_size[link]-1)) :

      # link state
      if (self.link_step[link] == self.link_size[link]) :
        self.link_step[link] = 0

      # node state
      self.node_conn[node] += 1
      self.__Step[node] = self.StepNodeConnect
      if (self.node_conn[node] == self.p_node2node[node+1]) :
        self.node_conn[node] = self.p_node2node[node]
        self.node_iter[node] += 1
        self.node_state[node] = NetSim.ST_WORK
        self.__Step[node] = self.StepNodeLocal
      else :
        print("[{:s}] [{:d}] {:4d}  -->|  {:d}".format(NetSim.CLASS_NAME,
              self.node_iter[node], node, self.node2node[self.node_conn[node]]))


    return

  # END def StepNodeTransfer (
#        self,
#        node ) :
  # ----------------------------------------------------------------------------

# END class NetSim ( object ) :
# ------------------------------------------------------------------------------