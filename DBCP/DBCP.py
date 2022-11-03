# Distance Between Coordinate Pairs (DBCP)
# Bradley Janocha (github.com/bradjano)
# Created: 11/03/2022
# Updated: 11/03/2022

# Import packages
import arcpy
import math

# Function to calculate the Haversine distance between two coordinate pairs
def apply_formula(fc):
    arcpy.management.AddField(fc, 'DIST', 'DOUBLE')
    arcpy.management.CalculateField(fc, 'DIST', expression, 'PYTHON3', codeblock)

# Optional function used to categorize GPS coordinates based on urban/rural class and distance
def categorize_gps(fc, field, thresh_u, thresh_r):
    # Add a field for the status
    arcpy.management.AddField(fc, 'Source', 'TEXT')
    arcpy.management.CalculateField(fc, 'Source', "'GPS'", 'PYTHON3')

    # Create a SQL query for urban households outside of the threshold
    whereclause = '"' + field + '"' + " = 'Urban' And " + '"DIST" > ' + str(thresh_u)
    print("Updating source for features that meet the following criteria: " + whereclause)

    # Use a cursor to select rural features with the SQL query
    with arcpy.da.UpdateCursor(fc, 'Source', whereclause) as cursor:
        for row in cursor:
            row[0] = 'INSPECT'
            cursor.updateRow(row)

    # Create a SQL query for rural households outside of the threshold
    whereclause = '"' + field + '"' + " = 'Rural' And " + '"DIST" > ' + str(thresh_r)
    print("Updating source for features that meet the following criteria: " + whereclause)

    # Use a cursor to select rural features with the SQL query
    with arcpy.da.UpdateCursor(fc, 'Source', whereclause) as cursor:
        for row in cursor:
            row[0] = 'INSPECT'
            cursor.updateRow(row)

if __name__ == '__main__':

    # Set up primary variables
    input_data = arcpy.GetParameterAsText(0)
    hh_lat = arcpy.GetParameterAsText(1)
    hh_long = arcpy.GetParameterAsText(2)
    clust_lat = arcpy.GetParameterAsText(3)
    clust_long = arcpy.GetParameterAsText(4)

    # Set up optional variables
    threshold_option = arcpy.GetParameter(5)
    urban_rural = arcpy.GetParameterAsText(6)
    thresh_urban = arcpy.GetParameter(7)
    thresh_rural = arcpy.GetParameter(8)

    # Function to calculate Haversine distance written as a block of code
    codeblock = """def haversine(lat1, lon1, lat2, lon2):

        dist_lat = (lat2 - lat1) * math.pi / 180
        dist_lon = (lon2 - lon1) * math.pi / 180

        lat1_radian = lat1 * math.pi / 180
        lat2_radian = lat2 * math.pi / 180

        a = (pow(math.sin(dist_lat / 2), 2) + pow(math.sin(dist_lon / 2), 2) * math.cos(lat1) * math.cos(lat2))
        c = 2 * math.asin(math.sqrt(a))
        earth_radius = 6371

        return earth_radius * c"""

    # Expression used to calculate field
    expression = 'haversine(!' + hh_lat + '!, !' + hh_long + '!, !' + clust_lat + '!, !' + clust_long + '!)'

    apply_formula(input_data)

    if threshold_option == 1:
        categorize_gps(input_data, urban_rural, thresh_urban, thresh_rural)