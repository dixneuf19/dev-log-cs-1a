# -*- coding: utf-8 -*-

##
# @author G. Gbikpi-Benissan, MRG, CentraleSupelec, France.
# @date 2016-02-10, 2016-02-20
# @version 1.0
#
# @class MeshViz
#

# -- Third-party modules
from vtk import vtkDataSetMapper
from vtk import vtkActor
from vtk import vtkRenderer
from vtk import vtkRenderWindow
from vtk import vtkLightKit
from vtk import vtkColorTransferFunction
from vtk import vtkGlyph3D
from vtk import vtkPolyDataMapper
from vtk import vtkGenericDataObjectReader
from vtk import vtkSphereSource
from vtk import vtkDoubleArray
from vtk import vtkDataObject
from vtk import vtkRenderWindowInteractor
from vtk import vtkWindowToImageFilter
from vtk import vtkJPEGWriter
from vtk import vtkPNGWriter

##
# @brief A VTK-based interactive tool for mesh visualization.
#
class MeshViz ( object ) :

  # ----------------------------------------------------------------------------
  # -- CLASS ATTRIBUTES
  # ----------------------------------------------------------------------------

  # Error status
  SUCCESS = 0
  FAILURE = 1

  # Class description
  CLASS_NAME = "MeshViz"
  CLASS_AUTHOR = "G. G.-Benissan, MRG, CentraleSupelec, France."
  METHODS = """
  __init__ ( self )
  Config (
        self,
        bg_color = (0,0,0),
        win_size = (800, 600),
        win_pos = (20, 50),
        cam_azimuth = 0,
        cam_elevation = 0,
        cam_zoom = 1 )

  ReadMeshFromFile (
        self,
        file_name )
  WriteScreenshotToFile (
        self,
        file_name,
        file_format = "jpg" )

  SelectPointData (
        self,
        array_name )
  SelectCellData (
        self,
        array_name )

  BuildPointColorScale (
        self,
        min_value,
        max_value,
        scale_type = "rainbow" )
  BuildCellColorScale (
        self,
        min_value,
        max_value,
        scale_type = "rainbow" )
  BuildGlyph (
        self,
        sphere_radius )

  Render (
        self,
        point_data,
        cell_data )
  IRender (
        self,
        point_data,
        cell_data )
  Close ( self )
  """

  # ----------------------------------------------------------------------------
  # -- INITIALIZATION
  # ----------------------------------------------------------------------------

  def __init__ ( self ) :

    # -- Dataset
    self.mesh = vtkDataObject()
    self.numb_point = 0
    self.numb_cell = 0

    # -- Visualization
    self.point_data = vtkDoubleArray()
    self.cell_data = vtkDoubleArray()
    self.point_dname = ""
    self.cell_dname = ""
    self.point_cscale = vtkColorTransferFunction()
    self.cell_cscale = vtkColorTransferFunction()
    self.glyph = vtkGlyph3D()

    # -- Display

    # 3D scene
    self.renderer = vtkRenderer()
    self.window = vtkRenderWindow()
    self.window.AddRenderer(self.renderer)

    # Mesh
    self.mesh_actor = vtkActor()
    self.renderer.AddActor(self.mesh_actor)

    # Glyph
    self.glyph_actor = vtkActor()
    self.renderer.AddActor(self.glyph_actor)

    # Light (paraview)
    light = vtkLightKit()
    light.AddLightsToRenderer(self.renderer)
    light.SetKeyLightWarmth(0.6)
    light.SetKeyLightIntensity(0.75)
    light.SetKeyLightElevation(50.0)
    light.SetKeyLightAzimuth(10.0)
    light.SetFillLightWarmth(0.4)
    light.SetFillLightElevation(-75.0)
    light.SetFillLightAzimuth(-10.0)
    light.SetKeyToFillRatio(3.0)
    light.SetBackLightWarmth(0.5)
    light.SetBackLightElevation(0.0)
    light.SetBackLightAzimuth(110.0)
    light.SetKeyToBackRatio(3.5)
    light.SetHeadLightWarmth(0.5)
    light.SetKeyToHeadRatio(3.0)
    light.MaintainLuminanceOff()

    # Camera
    self.camera = self.renderer.GetActiveCamera()
    self.cam_zoom = 1

    # -- Screenshot
    self.jpg_writer = vtkJPEGWriter()
    self.png_writer = vtkPNGWriter()

    # -- Error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""


  #enddef __init__ ( self )
  # ----------------------------------------------------------------------------

  ##
  # @brief Sets display options.
  # @param bg_color = background RGB color (default: (0,0,0)).
  #                 (r,g,b) := (0,0,0)..(1,1,1)
  # @param win_size = size of the display window (default: (800, 600)).
  # @param win_pos = position (default: (20, 50)).
  # @param cam_azimuth = horizontal rotation angle of the camera (in degree).
  # @param cam_elevation = vertical rotation.
  #                      (default angles: 0)
  # @param cam_zoom = camera zoom factor (default: 1).
  #
  def Config (
        self,
        bg_color = (0,0,0),
        win_size = (800, 600),
        win_pos = (20, 50),
        cam_azimuth = 0,
        cam_elevation = 0,
        cam_zoom = 1 ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # 3D scene
    self.renderer.SetBackground(bg_color[0], bg_color[1], bg_color[2])
    self.window.SetSize(win_size[0], win_size[1])
    self.window.SetPosition(win_pos[0], win_pos[1])

    # Camera
    self.camera.Azimuth(cam_azimuth)
    self.camera.Elevation(cam_elevation)
    self.camera.OrthogonalizeViewUp()
    self.cam_zoom = cam_zoom

    return

  #enddef Config (
#        self,
#        bg_color = (0,0,0),
#        win_size = (800, 600),
#        win_pos = (20, 50),
#        cam_azimuth = 0,
#        cam_elevation = 0,
#        cam_zoom = 1 )
  # ----------------------------------------------------------------------------

  ##
  # @brief Hides the display window.
  def Hide ( self ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # -- hide
    self.window.OffScreenRenderingOn()

    return

  #enddef Hide ( self )
  # ----------------------------------------------------------------------------

  # ----------------------------------------------------------------------------
  # -- FILE I/O
  # ----------------------------------------------------------------------------

  ##
  # @brief Reads mesh dataset from a file.
  # @param file_name = full name to the file.
  #
  def ReadMeshFromFile (
        self,
        file_name ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # output
    self.mesh = vtkDataObject()
    self.numb_point = 0
    self.numb_cell = 0

    # -- read dataset
    reader = vtkGenericDataObjectReader()
    reader.SetFileName(file_name)
    reader.Update()
    self.mesh = reader.GetOutput()
    self.numb_point = self.mesh.GetNumberOfElements(vtkDataObject.POINT)
    self.numb_cell = self.mesh.GetNumberOfElements(vtkDataObject.CELL)

    return

  #enddef ReadMeshFromFile (
#        self,
#        file_name )
  # ----------------------------------------------------------------------------

  ##
  # @brief Writes the 3D scene screenshot to file.
  # @param file_name = full name to the file.
  # @param file_format = image file format (default: "jpg").
  #                    {"jpg"|"png"}
  # @param img_zoom = screenshot zoom factor (default: 1).
  #
  def WriteScreenshotToFile (
        self,
        file_name,
        file_format = "jpg",
        img_zoom = 1 ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + MeshViz.CLASS_NAME + ".WriteScreenshotToFile]"

    # args
    file_format = file_format.lower().strip()

    # -- build screenshot
    img_filter = vtkWindowToImageFilter()
    img_filter.SetInput(self.window)
    img_filter.SetMagnification(img_zoom)
    img_filter.Update()

    # -- select image writer
    if (file_format == "jpg") :
      img_writer = self.jpg_writer
    elif (file_format == "png") :
      img_writer = self.png_writer
    else :
      self.err_code = MeshViz.FAILURE
      self.err_msg = err_header + "*** Error: " + file_format
      self.err_msg += " image format not supported."
      return

    # -- write to file
    img_writer.SetFileName(file_name)
    img_writer.SetInputData(img_filter.GetOutput())
    img_writer.Write()

    return

  #enddef WriteScreenshotToFile (
#        self,
#        file_name,
#        file_format = "jpg" )
  # ----------------------------------------------------------------------------

  # ----------------------------------------------------------------------------
  # -- VISUALIZATION
  # ----------------------------------------------------------------------------

  ##
  # @brief Selects the point data array to be visualized.
  # @param array_name = name of the array in the VTK file.
  #
  def SelectPointData (
        self,
        array_name ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # input
    self.point_dname = array_name

    # -- select array
    self.mesh.GetPointData().SetActiveScalars(self.point_dname)

    # -- get array
    self.point_data = self.mesh.GetPointData().GetArray(self.point_dname)

    return

  #enddef SelectPointData (
#        self,
#        array_name )
  # ----------------------------------------------------------------------------

  ##
  # @brief Selects the cell data array to be visualized.
  # @remarks See SelectPointData.
  #
  def SelectCellData (
        self,
        array_name ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # input
    self.cell_dname = array_name

    # -- select array
    self.mesh.GetCellData().SetActiveScalars(self.cell_dname)

    # -- get array
    self.cell_data = self.mesh.GetCellData().GetArray(self.cell_dname)

    return

  #enddef SelectCellData (
#        self,
#        array_name )
  # ----------------------------------------------------------------------------

  ##
  # @brief Generates a colors scale for point data.
  # @see BuildColorScale
  #
  def BuildPointColorScale (
        self,
        min_value,
        max_value,
        scale_type = "rainbow" ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + MeshViz.CLASS_NAME + ".BuildPointColorScale]"

    # -- build

    self.point_cscale = self.BuildColorScale(min_value, max_value, scale_type)
    if (self.err_code == MeshViz.FAILURE) :
      self.err_msg = err_header + "\n" + self.err_msg
      return


    return

  #enddef BuildPointColorScale (
#        self,
#        min_value,
#        max_value,
#        scale_type = "rainbow" )
  # ----------------------------------------------------------------------------

  ##
  # @brief Generates a colors scale for cell data.
  # @see BuildColorScale
  #
  def BuildCellColorScale (
        self,
        min_value,
        max_value,
        scale_type = "rainbow" ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + MeshViz.CLASS_NAME + ".BuildPointColorScale]"

    # -- build

    self.cell_cscale = self.BuildColorScale(min_value, max_value, scale_type)
    if (self.err_code == MeshViz.FAILURE) :
      self.err_msg = err_header + "\n" + self.err_msg
      return


    return

  #enddef BuildCellColorScale (
#        self,
#        min_value,
#        max_value,
#        scale_type = "rainbow" )
  # ----------------------------------------------------------------------------

  ##
  # @brief Generates a colors scale according to a range of data values.
  # @param min_value = lowest data value used for the scaling.
  # @param max_value = highest data value used for the scaling.
  # @param scale_type = type of colors scale (default: "rainbow").
  #                   {"rainbow"|"cooltowarm"}
  # @return color_scale = colors scale (vtkColorTransferFunction)
  #
  def BuildColorScale (
        self,
        min_value,
        max_value,
        scale_type = "rainbow" ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + MeshViz.CLASS_NAME + ".BuildColorScale]"

    # output
    color_scale = vtkColorTransferFunction()

    # args
    scale_type = scale_type.lower().strip()

    # -- build

    # rainbow scaling
    if (scale_type == "rainbow") :
      color_scale = self.BuildColorScaleRB(min_value, max_value)
      if (self.err_code == MeshViz.FAILURE) :
        self.err_msg = err_header + "\n" + self.err_msg
        return

    # cooltowarm scaling
    elif (scale_type == "cooltowarm") :
      color_scale = self.BuildColorScaleCTW(min_value, max_value)
      if (self.err_code == MeshViz.FAILURE) :
        self.err_msg = err_header + "\n" + self.err_msg
        return

    # -- handle scale type error
    else :
      self.err_code = MeshViz.FAILURE
      self.err_msg = err_header + "*** Error: " + scale_type
      self.err_msg += " scaling not supported."


    return color_scale

  #enddef BuildColorScale (
#        self,
#        min_value,
#        max_value,
#        scale_type = "rainbow" )
  # ----------------------------------------------------------------------------

  ##
  # @brief Generates "rainbow" colors scale.
  # @remarks see BuildColorScale.
  #
  def BuildColorScaleRB (
        self,
        min_value,
        max_value ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # -- set colors range (hsv)
    c = [(0.66667, 1, 1), (0, 1, 1)]

    # -- build scale
    color_scale = vtkColorTransferFunction()
    color_scale.SetColorSpaceToHSV()
    color_scale.HSVWrapOff()
    color_scale.AddHSVPoint(min_value, c[0][0], c[0][1], c[0][2])
    color_scale.AddHSVPoint(max_value, c[1][0], c[1][1], c[1][2])

    return color_scale

  #enddef BuildColorScaleRB (
#        self,
#        min_value,
#        max_value )
  # ----------------------------------------------------------------------------

  ##
  # @brief Generates "cooltowarm" colors scale.
  # @remarks see BuildColorScale.
  #
  def BuildColorScaleCTW (
        self,
        min_value,
        max_value ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # -- set colors range (rgb)
    c = [(59/255, 76/255, 192/255), (180/255, 4/255, 38/255)]

    # -- build scale
    color_scale = vtkColorTransferFunction()
    color_scale.SetColorSpaceToDiverging()
    color_scale.AddRGBPoint(min_value, c[0][0], c[0][1], c[0][2])
    color_scale.AddRGBPoint(max_value, c[1][0], c[1][1], c[1][2])

    return color_scale

  #enddef BuildColorScaleCTW (
#        self,
#        min_value,
#        max_value )
  # ----------------------------------------------------------------------------

  ##
  # @brief Generates spherical glyphs from point data.
  # @param sphere_radius = radius of the spheres.
  #
  def BuildGlyph (
        self,
        sphere_radius ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # -- build sphere model
    sphere = vtkSphereSource()
    sphere.SetRadius(sphere_radius)
    sphere.SetThetaResolution(90)

    # -- build glyphs
    self.glyph.SetInputData(self.mesh)
    self.glyph.SetSourceConnection(sphere.GetOutputPort())
    self.glyph.ScalingOff()
    self.glyph.Update()

    return

  #enddef BuildGlyph (
#        self,
#        sphere_radius )
  # ----------------------------------------------------------------------------

  ##
  # @brief Renders 3D scene including data visualization.
  # @param point_data = new values for point data array (iterable object).
  # @param cell_data = new values for cell data array (iterable object).
  #
  def Render (
        self,
        point_data,
        cell_data ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # -- update

    # point data
    for i in range(0, self.numb_point) :
      self.point_data.SetTuple1(i, point_data[i])

    # cell data
    for i in range(0, self.numb_cell) :
      self.cell_data.SetTuple1(i, cell_data[i])

    # glyph
    self.mesh.GetPointData().SetActiveScalars(self.point_dname)
    self.glyph.Update()
    self.mesh.GetPointData().SetActiveScalars(None)

    # -- render

    # mesh
    mesh_mapper = vtkDataSetMapper()
    mesh_mapper.SetInputData(self.mesh)
    mesh_mapper.SetLookupTable(self.cell_cscale)
    mesh_mapper.UseLookupTableScalarRangeOn()
    self.mesh_actor.SetMapper(mesh_mapper)

    # glyph
    glyph_mapper = vtkPolyDataMapper()
    glyph_mapper.SetInputData(self.glyph.GetOutput())
    glyph_mapper.SetLookupTable(self.point_cscale)
    glyph_mapper.UseLookupTableScalarRangeOn()
    self.glyph_actor.SetMapper(glyph_mapper)

    # 3D scene
    self.window.Render()

    # camera
    self.renderer.ResetCamera()
    self.camera.Zoom(self.cam_zoom)

    return

  #enddef Render (
#        self,
#        point_data,
#        cell_data )
  # ----------------------------------------------------------------------------

  ##
  # @brief Renders interactive 3D scene.
  # @remarks See Render.
  #
  def IRender (
        self,
        point_data,
        cell_data ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""
    err_header = "*** [" + MeshViz.CLASS_NAME + ".IRender]"

    # -- render
    self.window.OffScreenRenderingOff()
    self.Render(point_data, cell_data)
    if (self.err_code == MeshViz.FAILURE) :
      self.err_msg = err_header + "\n" + self.err_msg
      return

    # -- interact
    interact = vtkRenderWindowInteractor()
    interact.SetRenderWindow(self.window)
    interact.Initialize()
    interact.Start()

    return

  #enddef IRender (
#        self,
#        point_data,
#        cell_data )
  # ----------------------------------------------------------------------------

  ##
  # @brief Closes the display window.
  #
  def Close ( self ) :

    # -- init

    # error handling
    self.err_code = MeshViz.SUCCESS
    self.err_msg = ""

    # -- close
    self.window.Finalize()

    return

  #enddef Close ( self )
  # ----------------------------------------------------------------------------

#endclass MeshViz ( object )
# ------------------------------------------------------------------------------