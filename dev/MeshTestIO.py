# -*- coding: utf-8 -*-

##
# @author Pr Magoules HPC Research Group, CentraleSupelec, France
# @author G. Gbikpi-Benissan
# @date 2015-12-18, 2015-12-18
# @date 2016-12-13, 2016-12-13
# @version 2.0 [Python 2.7]
#

# -- Standard modules
import sys
import time

# -- MRG modules
sys.path.append("mod")
from mesh import Mesh

# -- Constants

# Error
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Program description
PROG_NAME = "[MeshTestIO]"
MIN_ARGC = 1
HELP = """
  BRIEF: Tests file I/O operations of class Mesh.
  ARGS:
        [-h] # Displays this description.
"""

# -- main ----------------------------------------------------------------------
def main ( argv=[PROG_NAME] ) :

  # ----------------------------------------------------------------------------
  # -- INITIALIZATION
  # ----------------------------------------------------------------------------

  # -- Mesh handler
  dom = Mesh()

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

  # -- set input mesh file name (constant)
  im_file_name = "../data/in/MRG/AP3D-H0750B-S0-LGM16.vtk"

  # -- print help (-h)
  if ("-h" in argv[MIN_ARGC:]) :
    print HELP
    return EXIT_SUCCESS

  # ----------------------------------------------------------------------------
  # -- INPUT
  # ----------------------------------------------------------------------------

  # -- read mesh
  print PROG_NAME, "--- Reading mesh from", im_file_name
  dom.ReadFromFileVtk(im_file_name)
  if (dom.err_code == Mesh.FAILURE) :
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
  if ((dom.numb_node != 16)
      or (dom.node_coord[3,1] != 0.013433498318)
      or (dom.numb_elem != 49)
      or (dom.elem2node[dom.p_elem2node[32]+1] != 15)
      or (dom.elem_type[48] != 3)) :
    test_success = False

  # -- end time measurement

  # cpu timeCalcul distribué, cluster

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