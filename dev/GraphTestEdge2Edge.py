# -*- coding: utf-8 -*-

##
# @author Pr Magoules HPC Research Group, CentraleSupelec, France
# @author G. Gbikpi-Benissan
# @author Julen Dixneuf, IS1260-PC01, CentraleSupelec, France [TODO]
# @date 2016-01-02, 2016-01-02
# @date 2016-12-13, 2016-12-13
# @date 2016-12-13, 2017-01-31 [TODO]
# @version 2.0 [Python 2.7]
#

# -- Standard modules
import sys
import time

# -- Third-party modules
import numpy

# -- MRG modules
sys.path.append("mod")
from mesh import Mesh
from graph import Graph

# -- Constants

# Error
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Program description
PROG_NAME = "[GraphTestEdge2Edge]"
MIN_ARGC = 1
HELP = """
  BRIEF: Tests line graph building with class Graph.
  ARGS:
        [-h] # Displays this description.
"""

# -- main ----------------------------------------------------------------------
def main ( argv=[PROG_NAME] ) :

  # ----------------------------------------------------------------------------
  # -- INITIALIZATION
  # ----------------------------------------------------------------------------

  # -- Graph I/O handler
  dom_io = Mesh()

  # -- Test
  
  # Expected output values
  ref_e2e = numpy.array([ 1,  0,  2,  3,  4,  1,  3,  4,  8,  1,  2,  4,  5,  8,  9, 10,  1,
        2,  3,  5,  6,  7,  4,  6,  7,  3,  8,  9, 10,  4,  5,  7, 11, 13,
       14,  4,  5,  6, 10, 14, 15,  2,  3,  5,  9, 10,  3,  5,  8, 10, 15,
       16,  3,  5,  8,  9,  7, 14, 15, 12,  6, 13, 14, 11, 13,  6, 11, 14,
       12,  6, 11, 13,  7, 10, 15,  7, 10, 14,  9, 16,  9, 15]) # [TODO]
  ref_p_e2e = numpy.array([ 0,  1,  5,  9, 16, 22, 29, 35, 41, 46, 52, 59, 63, 65, 69, 75, 80,
       82]) # [TODO]
  
  # Test result
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
  ig_file_name = "../data/in/MRG/AP3D-H0750B-SS0-LGM12.vtk"

  # -- print help (-h)
  if ("-h" in argv[MIN_ARGC:]) :
    print HELP
    return EXIT_SUCCESS

  # ----------------------------------------------------------------------------
  # -- INPUT
  # ----------------------------------------------------------------------------

  # -- read graph
  print PROG_NAME, "--- Reading graph from", ig_file_name
  dom_io.ReadFromFileVtk(ig_file_name)
  if (dom_io.err_code == Mesh.FAILURE) :
    print PROG_NAME, dom_io.err_msg
    return EXIT_FAILURE

  # -- build graph handler
  dom = Graph(dom_io.numb_node,
              dom_io.numb_elem,
              dom_io.elem2node,
              dom_io.p_elem2node)

  # ----------------------------------------------------------------------------
  # -- PROCESS
  # ----------------------------------------------------------------------------

  # -- begin time measurement

  # cpu time
  cpu_btime = time.clock()

  # wall-clock time
  wclock_btime = time.time()

  # -- build line graph
  print PROG_NAME, "--- Building line graph"
  dom.BuildEdge2Edge()
  if (dom.err_code == Graph.FAILURE) :
    print PROG_NAME, dom.err_msg
    return EXIT_FAILURE

  # -- test
  print PROG_NAME, "--- Testing"
  if ((not numpy.array_equal(dom.edge2edge, ref_e2e))
      or (not numpy.array_equal(dom.p_edge2edge, ref_p_e2e))) :
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