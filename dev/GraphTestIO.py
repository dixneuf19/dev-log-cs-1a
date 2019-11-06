# -*- coding: utf-8 -*-

##
# @author Pr Magoules HPC Research Group, CentraleSupelec, France
# @author G. Gbikpi-Benissan
# @date 2016-01-02, 2016-01-02
# @date 2016-12-13, 2016-12-13
# @version 2.0 [Python 2.7]
#

# -- Standard modules
import sys
import time

# -- MRG modules
sys.path.append("mod")
from graph import Graph

# -- Constants

# Error
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Program description
PROG_NAME = "[GraphTestIO]"
MIN_ARGC = 1
HELP = """
  BRIEF: Tests file I/O operations of class Graph.
  ARGS:
        [-h] # Displays this description.
"""

# -- main ----------------------------------------------------------------------
def main ( argv=[PROG_NAME] ) :

  # ----------------------------------------------------------------------------
  # -- INITIALIZATION
  # ----------------------------------------------------------------------------

  # -- Graph handler
  dom = Graph()

  # -- Test result
  test_success = True

  # ----------------------------------------------------------------------------
  # -- ARGUMENTS
  # ----------------------------------------------------------------------------

  # -- check minimum number of arguments
  argc = len(argv)
  if (argc < MIN_ARGC) :
    print HELP
    return EXIT_FAILURE

  # -- set input graph file name (constant)
  ig_file_name = "../data/in/DSJ/DSJC250.5.col"

  # -- print help (-h)
  if ("-h" in argv[MIN_ARGC:]) :
    print HELP
    return EXIT_SUCCESS

  # ----------------------------------------------------------------------------
  # -- INPUT
  # ----------------------------------------------------------------------------

  # -- read graph
  print PROG_NAME, "--- Reading graph from", ig_file_name
  dom.ReadFromFileDimacs(ig_file_name)
  if (dom.err_code == Graph.FAILURE) :
    print PROG_NAME, dom.err_msg
    return EXIT_FAILURE

  # ----------------------------------------------------------------------------
  # -- PROCESS
  # ----------------------------------------------------------------------------

  # -- begin time measurement

  # cpu time
  cpu_btime = time.clock()

  # wall-clock time
  wclock_btime = time.time()

  # -- test
  print PROG_NAME, "--- Testing"
  if ((dom.numb_vert != 250)
      or (dom.numb_edge != 15668)
      or (dom.edge2vert[dom.p_edge2vert[10278]+1] != 105)) :
    test_success = False
  
  # -- end time measurement

  # cpu time
  cpu_etime = time.clock()

  # wall-clock time
  wclock_etime = time.time()

  # ----------------------------------------------------------------------------
  # -- OUTPUT
  # ----------------------------------------------------------------------------

  # -- print result
  if (test_success) :
    print PROG_NAME, "*** Result: SUCCESS"
  else :
    print PROG_NAME, "*** Result: FAILURE"

  # -- print time measurement
  print PROG_NAME, "*** CPU: {:.3f} sec.".format(cpu_etime - cpu_btime)
  print PROG_NAME,\
        "*** Wall-clock: {:.3f} sec.".format(wclock_etime - wclock_btime)


  return EXIT_SUCCESS

# END def main ( argc, argv ) :
# ------------------------------------------------------------------------------

if __name__ == "__main__" :
  main(sys.argv)