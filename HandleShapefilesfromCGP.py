# -------------------------------------------------------------------------------
# Name:         Shapefile to JSON
# Purpose:      The purpose of this script is to download a zip file that
#               contains a shipefile(s), unzip it, buffer where needed,
#               merge all the shapefiles together into one coverage polygon,
#               merge all the polygons together with a dissolve, then single
#               part to multipart the results.  Amounts of polygons and amounts
#               of vertices will be calculated to make sure that the amounts
#               are not too high, to be checked against later when scripts are
#               merged.
#
# Author:       Sean Eagles
#
# Created:      31-05-2021
# Copyright:    (c) seagles 2021
# Licence:      <your licence>
# -------------------------------------------------------------------------------

# import urllib2
from urllib.request import urlopen
from contextlib import closing
# import requests
import zipfile
# import StringIO
import arcpy
import os


# module to download zip files
def download_url(url, save_path):
    with closing(urlopen(url)) as dl_file:
        with open(save_path, 'wb') as out_file:
            out_file.write(dl_file.read())


def extract_zipfile(save_path, folder):
    with zipfile.ZipFile(save_path, 'r') as zip_ref:
        zip_ref.extractall(folder)
    print("Zip file folder extracted to: " + folder)


# module for listing all feature classes within a given geodatabase
def listFcsInGDB(gdb):
    arcpy.env.workspace = gdb
    print('Processing ', arcpy.env.workspace)

    fcs = []
    for fds in arcpy.ListDatasets('', 'feature') + ['']:
        for fc in arcpy.ListFeatureClasses('', '', fds):
            # yield os.path.join(fds, fc)
            fcs.append(os.path.join(fds, fc))
    return fcs


def create_shapefile(folder, ShapefileName):
    # Create a shapefile to merge everything
    arcpy.CreateFeatureclass_management(
        out_path=folder,
        out_name=ShapefileName,
        geometry_type="POLYGON",
        template="",
        has_m="DISABLED",
        has_z="DISABLED",
        spatial_reference="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision",
        config_keyword="",
        spatial_grid_1="0",
        spatial_grid_2="0",
        spatial_grid_3="0")


def polygonTransform(FeatureClass):
    # set polygons which will be used to dissolve and create multipart
    # polygons in a single shapefile
    dissolved = FeatureClass + "_dissolved"
    singlepart = FeatureClass + "_finished"

    # add field "merge"
    arcpy.AddField_management(
        in_table=FeatureClass,
        field_name="MERGE",
        field_type="TEXT",
        field_precision="",
        field_scale="",
        field_length="5",
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain="")

    print("Field Added")

    # calculate the merge field to value 1, so that every polygon is
    # a value of 1
    arcpy.CalculateField_management(
        in_table=FeatureClass,
        field="MERGE",
        expression="1",
        expression_type="VB",
        code_block="")

    print("Field Calculated")

    # dissolve based on the value 1 in 'merge' field
    arcpy.Dissolve_management(
        in_features=FeatureClass,
        out_feature_class=dissolved,
        dissolve_field="MERGE",
        statistics_fields="",
        multi_part="MULTI_PART",
        unsplit_lines="DISSOLVE_LINES")

    print("Features Dissolved")

    # similar to the explode tool, take all of the multipart polygons
    # and create single part polygons that are separate when not
    # attached to another polygon
    arcpy.MultipartToSinglepart_management(
        in_features=dissolved,
        out_feature_class=singlepart)

    print("Multi part to single part explosion")

    # Append the result into the shapefile that has all appended
    # polygons
    arcpy.Append_management(
        inputs=singlepart,
        target=ShapefileAll,
        schema_type="NO_TEST",
        field_mapping="",
        subtype="")


def pointTransform(FeatureClass):
    # set polygons which will be used to dissolve and create multipart
    # polygons in a single shapefile
    dissolved = FeatureClass + "_dissolved"
    singlepart = FeatureClass + "_finished"

    # add field "merge"
    arcpy.AddField_management(
        in_table=FeatureClass,
        field_name="MERGE",
        field_type="TEXT",
        field_precision="",
        field_scale="",
        field_length="5",
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain="")

    print("Field Added")

    # calculate the merge field to value 1, so that every polygon is
    # a value of 1
    arcpy.CalculateField_management(
        in_table=FeatureClass,
        field="MERGE", expression="1",
        expression_type="VB",
        code_block="")

    print("Field Calculated")

    # dissolve based on the value 1 in 'merge' field
    arcpy.Dissolve_management(
        in_features=FeatureClass,
        out_feature_class=dissolved,
        dissolve_field="MERGE",
        statistics_fields="",
        multi_part="MULTI_PART",
        unsplit_lines="DISSOLVE_LINES")

    print("Features Dissolved")

    # similar to the explode tool, take all of the multipart polygons
    # and create single part polygons that are separate when not
    # attached to another polygon
    arcpy.MultipartToSinglepart_management(
        in_features=dissolved,
        out_feature_class=singlepart)

    print("Multi part to single part explosion")

    # Append the result into the shapefile that has all appended
    # polygons
    arcpy.Append_management(
        inputs=singlepart,
        target=ShapefileAll,
        schema_type="NO_TEST",
        field_mapping="",
        subtype="")


def lineTransform(FeatureClass):
    # create a name for the buffer and singlepart polygons to be created
    buffer = FeatureClass + "_buffer"
    dissolved = FeatureClass + "_dissolved"
    singlepart = FeatureClass + "_finished"

    # run buffer on the feature class to create a polygon feature class
    arcpy.Buffer_analysis(
        in_features=Shapefile,
        out_feature_class=buffer,
        buffer_distance_or_field="5000 Meters",
        line_side="FULL", line_end_type="ROUND",
        dissolve_option="NONE",
        dissolve_field="", method="PLANAR")

    print("Buffer created for points - " + buffer)

    # add a field called "merge"
    arcpy.AddField_management(
        in_table=buffer,
        field_name="MERGE",
        field_type="TEXT",
        field_precision="",
        field_scale="",
        field_length="5",
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain="")

    # calculate the merge field to value 1
    arcpy.CalculateField_management(
        in_table=buffer, field="MERGE",
        expression="1",
        expression_type="VB",
        code_block="")

    print("Field Calculated")

    # dissolve the polygons based on the merge value of 1 creating one
    # multipart polygon
    arcpy.Dissolve_management(
        in_features=buffer,
        out_feature_class=dissolved,
        dissolve_field="MERGE",
        statistics_fields="",
        multi_part="MULTI_PART",
        unsplit_lines="DISSOLVE_LINES")

    print("Features Dissolved")

    # similar to the explode tool, take the multipart polygon that was
    # created and make it into singlepart seperate polygons
    arcpy.MultipartToSinglepart_management(
        in_features=dissolved,
        out_feature_class=singlepart)

    print("Multi part to single part explosion")

    # append the new polyons into the shapefile which contains all
    # polygons
    arcpy.Append_management(
        inputs=singlepart,
        target=ShapefileAll,
        schema_type="NO_TEST",
        field_mapping="",
        subtype="")


if __name__ == '__main__':
    folder = r"C:\Temp\Cambridge_indian_reserve"
    url = 'https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec/shp/ \
        Transport/canvec_250K_ON_Transport_shp.zip'
    save_path = r"C:\TEMP\download.zip"
    workspace = r"C:\TEMP\Cambridge_indian_reserve\canvec_250K_ON_Transport"
    ShapefileName = "Transport_1M_Merged.shp"
    ShapefileAll = folder + "\\" + ShapefileName
    Geodatabase_name = "Transportation"
    Geodatabase = workspace + "\\" + Geodatabase_name  + ".gdb"
    Geodatabase_basename = workspace + "\\" + Geodatabase_name

    download_url(url, save_path)
    extract_zipfile(save_path, folder)
    create_shapefile(folder, ShapefileName)

    arcpy.CreateFileGDB_management(
        out_folder_path=workspace,
        out_name=Geodatabase_name,
        out_version="CURRENT")

    ShapefileAllName = os.path.basename(ShapefileAll)
    print("Name = " + ShapefileAllName)
    BaseShapefileAllName = os.path.splitext(ShapefileAllName)[0]
    print("Shapefile All base name = " + BaseShapefileAllName)
    # create dissolve and singlepart shapefiles to complete the proceses on the
    # merged shapefile with everything in it
    ShapefileAll_Dissolve = folder + "\\" + BaseShapefileAllName + " \
        _dissolve.shp"
    ShapefileAll_SinglePart = folder + "\\" + BaseShapefileAllName + " \
        _singlepart.shp"

    arcpy.env.workspace = workspace

    # A list of shapefiles
    Shapefiles = arcpy.ListFeatureClasses()

    # Create feature classes in the geodatabase to run tools on
    for SHP in Shapefiles:
        # set up workspace, and shapefile name
        Shapefile = workspace + "\\" + SHP
        print("Shapefile: " + Shapefile)
        Name = os.path.basename(Shapefile)
        print("Name = " + Name)
        BaseName = os.path.splitext(Name)[0]
        print("BaseName = " + BaseName)

        arcpy.FeatureClassToFeatureClass_conversion(
            in_features=Shapefile,
            out_path=Geodatabase,
            out_name=BaseName,
            where_clause="",
            field_mapping="",
            config_keyword="")

    fcs = listFcsInGDB(Geodatabase)

    # Cycle through all feature classes in the geodatabase
    print("Cycle through feature classes in geodatabase")
    for fc in fcs:
        # set feature class location and name
        FeatureClass = Geodatabase + "\\" + fc
        print("Feature class: " + FeatureClass)

        # Describe a feature class
        desc = arcpy.Describe(FeatureClass)

        # Get the shape type (Polygon, Polyline) of the feature class
        type = desc.shapeType

        print(str(type))
        # If the type is polygon run through these instructions
        if type == "Polygon":
            polygonTransform(FeatureClass)

        # run these instructions if type is point
        elif type == "Point":
            pointTransform(FeatureClass)

        # run these instructions if type is point
        elif type == "Polyline":
            lineTransform(FeatureClass)

    # now work on the master shapefile
    # add a field called "merge"
    arcpy.AddField_management(
        in_table=ShapefileAll,
        field_name="MERGE",
        field_type="TEXT",
        field_precision="",
        field_scale="",
        field_length="5",
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain="")

    print("Field Added")

    # calculate the merge field to value 1
    arcpy.CalculateField_management(
        in_table=ShapefileAll,
        field="MERGE",
        expression="1",
        expression_type="VB",
        code_block="")

    print("Field Calculated")

    # dissolve the polygons based on the merge value of 1 creating one
    # multipart polygon
    dissolve = "C:/TEMP/Map_Selection_Dissolve.shp"
    arcpy.Dissolve_management(
        in_features=ShapefileAll,
        out_feature_class=dissolve,
        dissolve_field="MERGE",
        statistics_fields="",
        multi_part="MULTI_PART",
        unsplit_lines="DISSOLVE_LINES")

    print("Features Dissolved")

    # take the dissolved polygon and explode the single polygon into singlepart
    # polygons
    singlepart = "C:/TEMP/MAP_Selection_Finished.shp"
    arcpy.MultipartToSinglepart_management(
        in_features=ShapefileAll,
        out_feature_class=singlepart)

    print("Multi part to single part explosion")

    # Add a field to count vertices "vertices"
    arcpy.AddField_management(
        in_table=ShapefileAll,
        field_name="VERTICES",
        field_type="FLOAT",
        field_precision="255",
        field_scale="0",
        field_length="",
        field_alias="",
        field_is_nullable="NULLABLE",
        field_is_required="NON_REQUIRED",
        field_domain="")

    print("Added field VERTICES")

    # Calculate the vertices field with a count of vertices in that polygon
    arcpy.CalculateField_management(
        ShapefileAll, "VERTICES",
        "!Shape!.pointCount-!Shape!.partCount",
        "PYTHON")

    print("Calculate the amount of vertices in VERTICES field")

    # print the count of all polygons found within the master shapefile
    PolygonCounter = 0
    with arcpy.da.SearchCursor(ShapefileAll, "MERGE") as cursor:
        for row in cursor:
            PolygonCounter = PolygonCounter + 1
    print("There are " + str(PolygonCounter) + " polygons")
    del row, cursor, PolygonCounter

    # create an ESRI GeoJSON for the master shapefile to be used to load into
    # GeoCore
    arcpy.FeaturesToJSON_conversion(
        in_features=ShapefileAll,
        out_json_file="C:/TEMP/IPN_FeaturesToJSON.json",
        format_json="FORMATTED",
        include_z_values="NO_Z_VALUES",
        include_m_values="NO_M_VALUES",
        geoJSON="GEOJSON")

    print("ESRI JSON created")

    arcpy.Delete_management(folder)
    arcpy.Delete_management(dissolve)
    arcpy.Delete_management(singlepart)
    arcpy.Delete_management(save_path)
