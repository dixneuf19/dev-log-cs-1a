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
PROG_NAME = "[GraphTestVertDegree]"
MIN_ARGC = 1
HELP = """
  BRIEF: Tests three different ways of vertex degrees building with class Graph.
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
  ref_degree = numpy.array([1, 2, 4, 4, 2, 5, 2, 4, 2, 4, 3, 1]) 
  
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
  
  # Graph.BulldVertDegree() use in order of priority vert2vert, 
  # vert2edge and edge2vert  
  
  # -- build line graph with edge2vert
  print PROG_NAME, "--- Building vertex degrees with edge2vert"
  dom.BuildVertDegree()
  vert_degree_edge2vert = dom.vert_degree
  if (dom.err_code == Graph.FAILURE) :
    print PROG_NAME, dom.err_msg
    return EXIT_FAILURE

# -- build line graph with vert2edge
  print PROG_NAME, "--- Building vertex degrees with vert2edge"
  dom.BuildVert2Edge()
  dom.BuildVertDegree()
  vert_degree_vert2edge = dom.vert_degree
  if (dom.err_code == Graph.FAILURE) :
    print PROG_NAME, dom.err_msg
    return EXIT_FAILURE
    
    # -- build line graph with vert2vert
  print PROG_NAME, "--- Building vertex degrees with vert2vert"
  dom.BuildVert2Vert()
  dom.BuildVertDegree()
  vert_degree_vert2vert = dom.vert_degree
  if (dom.err_code == Graph.FAILURE) :
    print PROG_NAME, dom.err_msg
    return EXIT_FAILURE
    
    
  # -- test
  print PROG_NAME, "--- Testing"
  if ((not numpy.array_equal(vert_degree_edge2vert, ref_degree))
      or (not numpy.array_equal(vert_degree_vert2edge, ref_degree))
      or (not numpy.array_equal(vert_degree_vert2vert, ref_degree))) :
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