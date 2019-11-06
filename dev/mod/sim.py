# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 16:30:59 2017

@author: 19jun
"""
import sys

from graph import Graph
from mesh import Mesh
#import scipy
from netsim import NetSim
from meshviz import MeshViz

def main(argv):
    
    
    
    
    path_to_file = "../../data/in/MRG/AP3D-H0750B-SS0-LGM12.vtk"
	# Create the Mesh object
    m = Mesh()
    print('Read VTK file')
	# Import the file into Mesh object
    m.ReadFromFileVtk(path_to_file)
    
    if m.err_code == 1:
        print(m.err_msg)
    
    print('Create the graph')
    
	# Create a Graph object with the attribute read by Mesh
    g = Graph(m.numb_node,        # numb_vert
                  m.numb_elem,    # numb_edge
                  m.elem2node,    # edge2vert
                  m.p_elem2node)  # p_edge2vert
    
	# create line graph, with numb_edge, numb_vert, vert2edge, p_vert2edge

	# create vert2edge
    print('Build edge2edge')
    g.BuildEdge2Edge()

	# build line graph
    
	print('Build line graph')
	lg = Graph()

	lg.numb_vert = g.numb_edge
	lg.numb_edge = g.numb_vert
	lg.vert2vert = g.edge2edge
	lg.p_vert2vert = g.p_edge2edge

			  
	# coloring edges, which are vertex of line graph
	print('Color edges of line graph')
	lg.ColorVertByWelshPowell()

	# adding edges colors to the graph

	print('Adding edges colors to the graph')
	g.edge_color = lg.vert_color


	# sort edges by color
	print('Sort edges by color')
	g.SortVert2EdgeByColor()
    
    # build sorted vert2vert
    print("Build sorted vert2vert")
    g.BuildVert2Vert()
    
    # Create first simulation
    print("Simulation")
    s1 = NetSim(g.numb_vert, g.numb_edge, g.vert2edge, g.vert2vert, g.p_vert2vert, numb_iter=3)
    s1.node_size = m.ReadFieldFromFileVtkAscii(path_to_file, 'subdomain_numb_nodes')[:,0]
    s1.link_size = m.ReadFieldFromFileVtkAscii(path_to_file, 'subdomain2numb_interface_node')[:,0]
	# [:, 0] transform a 2D numpy.array into a 1D numpy.array
	
	# Prepare the vizualisation

	# Create the MeshViz object
    viz = MeshViz()
	# Import the file
    viz.ReadMeshFromFile(path_to_file)
    viz.SelectCellData('subdomain2numb_interface_node')
    viz.SelectPointData('subdomain_numb_nodes')
	# Set the background color to white
    viz.Config()
	# Find the extrema for the size of nodes and links
    point_data, cell_data = s1.node_size, s1.link_size
    min_point, max_point = 0, max(point_data)
    min_cell, max_cell = 0, max(cell_data)
    
    # small fix to not render all the step at the beginning
    acc = 100
    first_com = min(point_data) - 0.5*acc
    
    # Set the ColorScale
    viz.BuildCellColorScale(min_cell, max_cell)
    viz.BuildPointColorScale(min_point, max_point)
	# Select the radius of the sphere for nodes
    viz.BuildGlyph(0.7)
    
    output = '../../data/out/test'
    
    #import time
    i = 0
    
    
    while not(s1.flag_end):
        print(i)
        if i < first_com:
            for t in range(acc):
                s1.Step()
            point_data, cell_data = s1.node_step, s1.link_step
            viz.Render(point_data, cell_data)
            i += acc
        else:
            point_data, cell_data = s1.node_step, s1.link_step
            viz.Render(point_data, cell_data)
            s1.Step()
            i += 1
            
    
        viz.WriteScreenshotToFile(output + str(i) + '.jpg')
        
        
        
        
    viz.Close()

#    while not(s1.flag_end):
#        s1.Step()
#
#    print(s1.numb_step)

if __name__ == "__main__" :
    main(sys.argv)





