from typing import List, Optional, Dict, Iterable, Any, overload
import io
import collections.abc
from collections.abc import Sequence
from datetime import datetime
from aspose.pyreflection import Type
import aspose.pycore
import aspose.pydrawing
from uuid import UUID
import aspose.gis
import aspose.gis.common
import aspose.gis.common.formats
import aspose.gis.common.formats.dbase
import aspose.gis.common.formats.gdbtable
import aspose.gis.common.formats.mapinfo
import aspose.gis.common.formats.mapinfo.graphicalobjects
import aspose.gis.common.formats.mapinfo.interchangeformat
import aspose.gis.common.formats.mapinfo.styling
import aspose.gis.common.formats.mapinfo.tabformat
import aspose.gis.common.formats.mapinfo.tabformat.map
import aspose.gis.common.formats.wkb
import aspose.gis.common.formats.wkt
import aspose.gis.common.formats.xml
import aspose.gis.common.io
import aspose.gis.epsg
import aspose.gis.formats
import aspose.gis.formats.bmpw
import aspose.gis.formats.csv
import aspose.gis.formats.database
import aspose.gis.formats.database.dataediting
import aspose.gis.formats.database.fromdefinition
import aspose.gis.formats.esriascii
import aspose.gis.formats.esrijson
import aspose.gis.formats.filegdb
import aspose.gis.formats.gdal
import aspose.gis.formats.geojson
import aspose.gis.formats.geojsonseq
import aspose.gis.formats.geopackage
import aspose.gis.formats.geotiff
import aspose.gis.formats.gml
import aspose.gis.formats.gpx
import aspose.gis.formats.infile
import aspose.gis.formats.inmemory
import aspose.gis.formats.jpegw
import aspose.gis.formats.kml
import aspose.gis.formats.kml.specificfields
import aspose.gis.formats.kml.styles
import aspose.gis.formats.mapinfointerchange
import aspose.gis.formats.mapinfotab
import aspose.gis.formats.osmxml
import aspose.gis.formats.pngw
import aspose.gis.formats.postgis
import aspose.gis.formats.shapefile
import aspose.gis.formats.sqlserver
import aspose.gis.formats.tiffw
import aspose.gis.formats.topojson
import aspose.gis.formats.worldfile
import aspose.gis.formats.xyztile
import aspose.gis.geometries
import aspose.gis.geotools
import aspose.gis.geotools.extensions
import aspose.gis.geotools.layersmap
import aspose.gis.geotools.mapbuilder
import aspose.gis.geotools.wayanalyzer
import aspose.gis.imagemetadata
import aspose.gis.indexing
import aspose.gis.indexing.bplustree
import aspose.gis.indexing.qixtree
import aspose.gis.indexing.rtree
import aspose.gis.labeling
import aspose.gis.labeling.line
import aspose.gis.painting
import aspose.gis.projections
import aspose.gis.raster
import aspose.gis.raster.web
import aspose.gis.relationship
import aspose.gis.relationship.joins
import aspose.gis.rendering
import aspose.gis.rendering.colorizers
import aspose.gis.rendering.formats
import aspose.gis.rendering.formats.bmp
import aspose.gis.rendering.formats.jpeg
import aspose.gis.rendering.formats.png
import aspose.gis.rendering.formats.svg
import aspose.gis.rendering.labelings
import aspose.gis.rendering.sld
import aspose.gis.rendering.symbolizers
import aspose.gis.spatialreferencing
import aspose.gis.topology
import aspose.gis.topology.algorithms
import aspose.gis.topology.buffer
import aspose.gis.topology.graph

class SqlServerDriver(aspose.gis.DatabaseDriver):
    '''A driver for the SQL Server database.'''
    

class SqlServerOptions(aspose.gis.DatabaseDriverOptions):
    '''Driver-specific options for SqlServer format.
    At the moment, the driver provides no customizable options.'''
    
    def __init__(self) -> None:
        '''Create new instance.'''
        raise NotImplementedError()
    
    @property
    def validate_geometries_on_write(self) -> bool:
        '''Determines if geometries should be validated when they are added to the layer.
        If set to , :py:attr:`aspose.gis.geometries.Geometry.is_valid` is called for each
        geometry when it\'s added to the layer, and if validation fails (:py:attr:`aspose.gis.geometries.Geometry.is_valid` is ), :py:class:`aspose.gis.GisException` is thrown.'''
        raise NotImplementedError()
    
    @validate_geometries_on_write.setter
    def validate_geometries_on_write(self, value : bool) -> None:
        '''Determines if geometries should be validated when they are added to the layer.
        If set to , :py:attr:`aspose.gis.geometries.Geometry.is_valid` is called for each
        geometry when it\'s added to the layer, and if validation fails (:py:attr:`aspose.gis.geometries.Geometry.is_valid` is ), :py:class:`aspose.gis.GisException` is thrown.'''
        raise NotImplementedError()
    
    @property
    def write_polygons_as_lines(self) -> bool:
        '''Determines if transformation of polygon or multipolygon to linestring is allowed. Defaults to .'''
        raise NotImplementedError()
    
    @write_polygons_as_lines.setter
    def write_polygons_as_lines(self, value : bool) -> None:
        '''Determines if transformation of polygon or multipolygon to linestring is allowed. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def create_midpoints(self) -> bool:
        '''Determines if add a new point in the middle to each segment of geometry. Defaults to .'''
        raise NotImplementedError()
    
    @create_midpoints.setter
    def create_midpoints(self, value : bool) -> None:
        '''Determines if add a new point in the middle to each segment of geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def close_linear_ring(self) -> bool:
        '''Determines if close a unclosed :py:attr:`aspose.gis.geometries.GeometryType.LINEAR_RING` in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @close_linear_ring.setter
    def close_linear_ring(self, value : bool) -> None:
        '''Determines if close a unclosed :py:attr:`aspose.gis.geometries.GeometryType.LINEAR_RING` in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def delete_near_points(self) -> bool:
        '''Determines if delete near points in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @delete_near_points.setter
    def delete_near_points(self, value : bool) -> None:
        '''Determines if delete near points in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def delete_near_points_distance(self) -> float:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.delete_near_points`. Defaults to .'''
        raise NotImplementedError()
    
    @delete_near_points_distance.setter
    def delete_near_points_distance(self, value : float) -> None:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.delete_near_points`. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def simplify_segments(self) -> bool:
        '''Determines if delete points lying on the same segment in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @simplify_segments.setter
    def simplify_segments(self, value : bool) -> None:
        '''Determines if delete points lying on the same segment in each geometry. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def simplify_segments_distance(self) -> float:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.simplify_segments`. Defaults to .'''
        raise NotImplementedError()
    
    @simplify_segments_distance.setter
    def simplify_segments_distance(self, value : float) -> None:
        '''Determines distance for :py:attr:`aspose.gis.DriverOptions.simplify_segments`. Defaults to .'''
        raise NotImplementedError()
    
    @property
    def xy_precision_model(self) -> aspose.gis.PrecisionModel:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to X and Y coordinates
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @xy_precision_model.setter
    def xy_precision_model(self, value : aspose.gis.PrecisionModel) -> None:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to X and Y coordinates
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @property
    def z_precision_model(self) -> aspose.gis.PrecisionModel:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to Z coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @z_precision_model.setter
    def z_precision_model(self, value : aspose.gis.PrecisionModel) -> None:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to Z coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @property
    def m_precision_model(self) -> aspose.gis.PrecisionModel:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to M coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @m_precision_model.setter
    def m_precision_model(self, value : aspose.gis.PrecisionModel) -> None:
        '''A :py:class:`aspose.gis.PrecisionModel` that will be applied to M coordinate
        when geometries are added to the :py:class:`aspose.gis.VectorLayer` or when they are read from the :py:class:`aspose.gis.VectorLayer`.
        The default value is :py:attr:`aspose.gis.PrecisionModel.exact`.'''
        raise NotImplementedError()
    
    @property
    def linearization_tolerance(self) -> float:
        '''A tolerance to use to linearize curve geometries.'''
        raise NotImplementedError()
    
    @linearization_tolerance.setter
    def linearization_tolerance(self, value : float) -> None:
        '''A tolerance to use to linearize curve geometries.'''
        raise NotImplementedError()
    
    @property
    def spatial_reference_system_mode(self) -> aspose.gis.SpatialReferenceSystemMode:
        '''Determines how the unknown geometries\' SRS for the database should be handle when they are added to the layer.
        The default value is :py:attr:`aspose.gis.SpatialReferenceSystemMode.THROW_EXCEPTION`.'''
        raise NotImplementedError()
    
    @spatial_reference_system_mode.setter
    def spatial_reference_system_mode(self, value : aspose.gis.SpatialReferenceSystemMode) -> None:
        '''Determines how the unknown geometries\' SRS for the database should be handle when they are added to the layer.
        The default value is :py:attr:`aspose.gis.SpatialReferenceSystemMode.THROW_EXCEPTION`.'''
        raise NotImplementedError()
    

