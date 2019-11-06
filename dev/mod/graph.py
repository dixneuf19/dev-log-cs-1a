# -*- coding: utf-8 -*-

##
# @author Pr Magoules HPC Research Group, CentraleSupelec, France
# @author G. Gbikpi-Benissan
# @author Julen Dixneuf, IS1260-PC01, CentraleSupelec, France [DONE]
# @date 2015-12-11, 2016-02-08
# @date 2016-12-13, 2016-12-13
# @date 2016-12-13, 2017-02-23 [DONE]
# @version 2.0
#
# @class Graph
#

# -- Third-party modules
import numpy
import scipy.sparse
import Queue

##
# @brief A set of graph algorithms and basic operations.
#
# Currently:
# - File Input (DIMACS)
# - Line graph
# - Coloring (Welsh-Powell)
#
class Graph ( object ) :

  # ----------------------------------------------------------------------------
  # -- CLASS ATTRIBUTES
  # ----------------------------------------------------------------------------

  # Error status
  SUCCESS = 0
  FAILURE = 1

  # Class description
  CLASS_NAME = "Graph"
  CLASS_AUTHOR = "J. Dixneuf, IS1260-PC01, CentraleSupelec, France" # [DONE]
  METHODS = """
  __init__ (
        self,
        numb_vert = 0,
        numb_edge = 0,
        edge2vert = numpy.array([]),
        p_edge2vert = numpy.array([0]) )

  ReadFromFileDimacs (
        self,
        file_name,
        file_type = "ASCII" )
  ReadFromFileDimacsAscii (
        self,
        file_name )

  BuildEdge2Edge ( self )

  BuildVertDegree ( self )
  ColorVertByWelshPowell ( self )

  BuildVert2Edge ( self )
  SortVert2EdgeByColor ( self )
  BuildVert2Vert ( self )
  """

  # ----------------------------------------------------------------------------
  # -- INITIALIZATION
  # ----------------------------------------------------------------------------

  ##
  # @param numb_vert = number of vertices
  #             [default: 0]
  # @param numb_edge = number of edges
  #             [default: 0]
  # @param edge2vert = vertices of each edge (CSR storage)
  #             [default: numpy.array([])]
  # @param p_edge2vert = index of each edge in edge2vert (CSR storage)
  #             [default: numpy.array([0])]
  # @remarks There is not any copy of the input arrays.
  #
  def __init__ (
        self,
        numb_vert = 0,
        numb_edge = 0,
        edge2vert = numpy.array([]),
        p_edge2vert = numpy.array([0]) ) :

    # -- Dataset

    self.numb_vert = numb_vert
    self.numb_edge = numb_edge
    self.edge2vert = edge2vert
    self.p_edge2vert = p_edge2vert

    # -- Line graph

    # Adjacent edges of each edge (CSR storage)
    self.edge2edge = numpy.array([])
    self.p_edge2edge = numpy.array([0])

    # -- Graph coloring

    # Degree of each vertex
    self.vert_degree = numpy.array([])

    # Adjacent vertices of each vertex (CSR storage)
    self.vert2vert = numpy.array([])
    self.p_vert2vert = numpy.array([0])

    # Number of colors
    self.numb_color = 0

    # Color of each vertex
    self.vert_color = numpy.array([])

    # Color of each edge
    self.edge_color = numpy.array([])

    # -- Color-based reordering

    # Incident edges of each vertex (CSR storage)
    self.vert2edge = numpy.array([])
    self.p_vert2edge = numpy.array([0])

    # -- Error handling

    # Last error code
    self.err_code = Graph.SUCCESS

    # Last error message
    self.err_msg = ""

  # END def __init__ (
#        self,
#        numb_vert = 0,
#        numb_edge = 0,
#        edge2vert = numpy.array([]),
#        p_edge2vert = numpy.array([0]) ) :
  # ----------------------------------------------------------------------------

  # ----------------------------------------------------------------------------
  # -- FILE I/O
  # ----------------------------------------------------------------------------

  ##
  # @brief Reads graph dataset from a DIMACS edge problem file.
  # @param file_name = full name of the file (str)
  # @param file_type = numerical data format ("ASCII", "BINARY")
  #             [default: "ASCII"]
  #
  def ReadFromFileDimacs (
        self,
        file_name,
        file_type = "ASCII" ) :

    # -- init

    # error handling
    self.err_code = Graph.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + Graph.CLASS_NAME + ".ReadFromFileDimacs]"

    # -- read dataset
    if (file_type == "ASCII") :

      self.ReadFromFileDimacsAscii(file_name)
      if (self.err_code == Graph.FAILURE) :
        self.err_msg = err_header + "\n" + self.err_msg

    else :
      self.err_code = Graph.FAILURE
      self.err_msg = err_header + " Error: " + file_type + " file not supported"


    return

  # END def ReadFromFileDimacs (
#        self,
#        file_name,
#        file_type = "ASCII" ) :
  # ----------------------------------------------------------------------------

  ##
  # @brief Reads graph dataset from a DIMACS edge problem ASCII file.
  # @param file_name = full name of the file (str)
  #
  def ReadFromFileDimacsAscii (
        self,
        file_name ) :

    # -- init

    # error handling
    self.err_code = Graph.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + Graph.CLASS_NAME + ".ReadFromFileDimacsAscii]"

    # output
    self.numb_vert = 0
    self.numb_edge = 0
    self.edge2vert = numpy.array([])
    self.p_edge2vert = numpy.array([0])

    # -- open file
    try :
      p_file = open(file_name, "r")
    except :
      self.err_code = Graph.FAILURE
      self.err_msg = err_header + " Error: cannot open " + file_name
      return

    # -- read number of vertices and number of edges

    # read problem line (p edge numb_vert numb_edge)
    # [DONE] Environ 5 lignes

    # read the first character
    buf = p_file.read(1)
    while (buf not in {'c', ''}):
        buf = p_file.read(1)
        
    # skip all 'c' lines
    while (buf == 'c'):
        buf = p_file.readline()
        buf = p_file.read(1)
        
    #read first letter (p)
    while (buf not in {'p', ''}):
        buf = p_file.read(1)
    
    #read problem line
    buf = p_file.readline()
    

    # extract numbers
    buf = buf.split() # "1   2".split() != "1   2".split(' ')
    # [DONE] Environ 3 lignes
    self.numb_vert = int(buf[1])
    self.numb_edge = int(buf[2])

    # -- read edges vertices

    # init
    self.edge2vert = []
    self.p_edge2vert = [0]
    edge_count = 0

    # read edge descriptor lines (e vert1 vert2)
    # [DONE] Environ 12 lignes
    
    # read each edge
    buf = p_file.readline()
    while buf != '':
        
        buf = buf.split() #buf = ['e', vert1, vert2]
        self.edge2vert.append(int(buf[1])-1) # "-1" to start indexing at 0
        self.edge2vert.append(int(buf[2])-1)
        edge_count += 1
        self.p_edge2vert.append(edge_count*2)
        buf = p_file.readline()

    # -- convert to numpy.ndarray
    # [DONE] 2 ligne

    self.edge2vert = numpy.array(self.edge2vert)
    self.p_edge2vert = numpy.array(self.p_edge2vert)    
    
    
    # -- update number of edges
    # [DONE] 1 ligne
    self.numb_edge = edge_count

    # -- close file
    p_file.close()

    return

  # END def ReadFromFileDimacsAscii (
#        self,
#        file_name ) :
  # ----------------------------------------------------------------------------

  # ----------------------------------------------------------------------------
  # -- LINE GRAPH
  # ----------------------------------------------------------------------------

  ##
  # @brief Builds edge2edge and p_edge2edge.
  #
  def BuildEdge2Edge ( self ) :

    # -- init

    # error handling
    # [DONE] 3 lignes
    self.err_code = Graph.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + Graph.CLASS_NAME + ".BuildEdge2Edge]"
    
    # output
    self.edge2edge = numpy.array([])
    self.p_edge2edge = numpy.array([0])

    # -- check dependencies
    if (len(self.edge2vert) == 0) :
      self.err_code = Graph.FAILURE
      self.err_msg = err_header + " Error: edge2vert is required"
      return
    
    # -- build transpose of incidence matrix
    # [DONE] Environ 2 lignes
    # (voir les fonctions numpy.ones et scipy.sparse.csr_matrix)
    incidence_matrix_T = scipy.sparse.csr_matrix((numpy.ones(self.numb_edge*2),
                                                 self.edge2vert, 
                                                 self.p_edge2vert))
    
                                    
    # numpy.ones generates "1" for incidence matrix, two for each edges
                                                 
    
    
    # -- compute incidence matrix
    # [DONE] 1 ligne
    incidence_matrix = incidence_matrix_T.transpose()
    
    # -- build identity matrix
    # [DONE] 1 ligne
    # (voir liste des fonctions de scipy.sparse)
    identity_matrix = scipy.sparse.identity(self.numb_edge)

    # -- compute line graph adjacency matrix
    # [DONE] 1 ligne
    edge_incidence_matrix = (incidence_matrix_T.dot(incidence_matrix) - 
                            2 * identity_matrix)

    # -- extract edge2edge and p_edge2edge
    # [DONE] 2 lignes
    self.edge2edge = edge_incidence_matrix.indices
    self.p_edge2edge = edge_incidence_matrix.indptr
    

    return

  # END def BuildEdge2Edge ( self ) :
  # ----------------------------------------------------------------------------

  # ----------------------------------------------------------------------------
  # -- COLORING
  # ----------------------------------------------------------------------------

  ##
  # @brief Builds vert_degree.
  #
  def BuildVertDegree ( self ) :

    # -- init
    self.vert_degree = numpy.zeros(self.numb_vert, dtype=numpy.int)
    # [DONE]
    err_header = ""
    # -- check dependencies
    if ((len(self.edge2vert) == 0)
        and (len(self.vert2edge) == 0)
        and (len(self.vert2vert) == 0)) :
      self.err_code = Graph.FAILURE
      self.err_msg = err_header + " Error: either edge2vert or vert2edge"
      self.err_msg += " or vert2vert is required"
      return

    # -- build vert_degree

    # either build from vert2vert
    if (len(self.vert2vert) != 0) :
        
      # [DONE] Environ 3 lignes
        for i in range(self.numb_vert):
            self.vert_degree[i] = (self.p_vert2vert[i+1] - self.p_vert2vert[i])
            
    # or build from vert2edge
    elif (len(self.vert2edge) != 0) :
        
      # [DONE] Environ 3 lignes
        for i in range(self.numb_vert):
            self.vert_degree[i] = (self.p_vert2edge[i+1] - self.p_vert2edge[i])
            
    # or build from edge2vert
    else :
    
      # [DONE] Environ 3 lignes
        for x in self.edge2vert:
            self.vert_degree[x] += 1
            
    
    return

  # END def BuildVertDegree ( self ) :
  # ----------------------------------------------------------------------------

  ##
  # @brief Constructs a proper vertex coloring using Welsh-Powell algorithm.
  #
  def ColorVertByWelshPowell ( self ) :

    # [DONE]

    # -- init

    # error handling
    self.err_code = Graph.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + Graph.CLASS_NAME + ".ColorVertByWelshPowell]"
    
    #output
    self.numb_color = 0
    self.vert_color = -numpy.ones(self.numb_vert, dtype=numpy.int)
    # can't use zeros because '0' is a color, '-1' means colorless
    
    # -- check dependencies
    if (len(self.vert_degree) == 0) :
        self.BuildVertDegree()
      
    if (len(self.vert2vert) == 0) :
        self.BuildVert2Vert()
    
    
    # -- sort dec vertex by degree 
    # build an list of the indice of the sorted vertex
    # we're using a queue data-type for convenience
    
    indice_sorted = Queue.Queue(self.numb_vert)
    vert_sorted = numpy.zeros(self.numb_vert)
    for i in range(self.numb_vert):
        degree_max = 0
        indice_deg_max = -1
        for j in range(self.numb_vert):
            if vert_sorted[j] == 0:
                if self.vert_degree[j] > degree_max:
                    degree_max = self.vert_degree[j]
                    indice_deg_max = j
        indice_sorted.put(indice_deg_max)
        vert_sorted[indice_deg_max] = 1


    # not the best sorting algorithm in term of efficiency, but works anyway
        
    # -- coloring
    while not (indice_sorted.empty()): #run until all vertex colored
            
        # color the highest vertex
        self.vert_color[indice_sorted.get()] = self.numb_color
    
        numb_vert_uncolored = indice_sorted.qsize()
        # color other vertex if there is no conflicts, by highest degree
        for i in range(numb_vert_uncolored):
            
            # extracting the vertex
            vert = indice_sorted.get()
            
            # checking conflicts
            no_conflicts = True
            j = 0
            while ((j < self.vert_degree[vert]) and (no_conflicts)):
                # for all neigbour vertex, check if they have the same color
                
                if (self.vert_color[self.vert2vert[self.p_vert2vert[vert] + j]]
                      == self.numb_color  ):
                        
                        no_conflicts = False
                j+= 1
            
            
            if no_conflicts:
                # color the vertex
                self.vert_color[vert] = self.numb_color
                
            
            else:
                # put back the vertex in the queue, which stay sorted
                indice_sorted.put(vert)
            
                

        # select a new color (also works as a counter)
    
        self.numb_color += 1  
    

    return

  # END def ColorVertByWelshPowell ( self ) :
  # ----------------------------------------------------------------------------

  # ----------------------------------------------------------------------------
  # -- ORDERING
  # ----------------------------------------------------------------------------

  ##
  # @brief Builds vert2edge and p_vert2edge.
  #
  def BuildVert2Edge ( self ) :

    
    # -- init

    # error handling
    # [DONE] 3 lignes
    self.err_code = Graph.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + Graph.CLASS_NAME + ".BuildVert2Edge]"
    
    # output
    self.vert2edge = numpy.array([])
    self.p_vert2edge = numpy.array([0])

    # -- check dependencies
    if (len(self.edge2vert) == 0) :
      self.err_code = Graph.FAILURE
      self.err_msg = err_header + " Error: edge2vert is required"
      return
    
    # -- build transpose of incidence matrix
    
    incidence_matrix_T = scipy.sparse.csr_matrix((numpy.ones(self.numb_edge*2),
                                                 self.edge2vert, 
                                                 self.p_edge2vert))
    
    # numpy.ones generates "1" for incidence matrix, two for each edges
                                                 
    incidence_matrix = scipy.sparse.csr_matrix(incidence_matrix_T.transpose())
    
    
    # -- extract vert2vert and p_vert2vert

    self.vert2edge = incidence_matrix.indices
    self.p_vert2edge = incidence_matrix.indptr
    
    
    

    return

  # END def BuildVert2Edge ( self ) :
  # ----------------------------------------------------------------------------

  ##
  # @brief Sorts list of incident edges of each vertex (vert2edge), according
  #        to edge color.
  #
  def SortVert2EdgeByColor ( self ) :
      
    # [DONE]
    # -- init

    # error handling
    self.err_code = Graph.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + Graph.CLASS_NAME + ".SortVert2EdgeByColor]"
    

    # -- check dependencies
    if (len(self.edge_color) == 0) :
      self.err_code = Graph.FAILURE
      self.err_msg = err_header + " Error: edge_color is required"
      return
    
    
    if len(self.vert2edge) == 0:
        self.BuildVert2Edge()
        
    # -- sorting
    
    # choose a vertex
    for i in range(self.numb_vert):
        ind_start, ind_end = self.p_vert2edge[i], self.p_vert2edge[i+1]
        # sort his edges, using edge_color as key
        self.vert2edge[ind_start : ind_end] = sorted(self.vert2edge[ind_start:ind_end],
                                                    key=lambda j: self.edge_color[j])
        

    return

  # END def SortVert2EdgeByColor ( self ) :
  # ----------------------------------------------------------------------------

  ##
  # @brief Builds vert2vert and p_vert2vert
  #
  def BuildVert2Vert ( self ) :

    # [DONE]
    # -- init
    
    # error handling
    self.err_code = Graph.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + Graph.CLASS_NAME + ".BuildVert2Vert]"
    
    # output
    self.vert2vert = numpy.array([])
    self.p_vert2vert = numpy.array([0])

    # -- check dependencies
    
     
    if (len(self.vert_degree) == 0) :
        self.BuildVertDegree()
    
    # use vert2edge instead of edge2vert in case it has been sorted    
    
    if len(self.vert2edge) == 0:
        print('BuildVert2Edge')
        self.BuildVert2Edge()
    
    
    incidence_matrix = scipy.sparse.csr_matrix((numpy.ones(self.numb_edge*2),
                                                 self.vert2edge, 
                                                 self.p_vert2edge))
    
    # numpy.ones generates "1" for incidence matrix, two for each edges
    
    # -- build incidence matrix
    incidence_matrix_T = incidence_matrix.transpose()
    
    # -- build diagonal vertex degree matrix
    
    row = list(range(self.numb_vert))
    col = row
    
    vert_degree_diag_matrix = scipy.sparse.csr_matrix((self.vert_degree, (row,col)))

        
    

    # -- compute vertex graph adjacency matrix
    vert_incidence_matrix = (incidence_matrix.dot(incidence_matrix_T) - 
                            vert_degree_diag_matrix)
                            
    
    # -- extract vert2vert and p_vert2vert
    self.vert2vert = vert_incidence_matrix.indices
    self.p_vert2vert = vert_incidence_matrix.indptr
    

                                                 

    return

  # END def BuildVert2Vert ( self ) :
  # ----------------------------------------------------------------------------

# END class Graph ( object ) :
# ------------------------------------------------------------------------------