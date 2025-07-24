import geopandas as gpd
import ee

def load_shapefile_as_ee(filepath):
    """Restituisce una ee.Geometry per Earth Engine"""
    gdf = gpd.read_file(filepath).to_crs(epsg=4326)
    geom = gdf.geometry.unary_union
    return ee.Geometry(geom.__geo_interface__)

def load_shapefile_as_gdf(filepath):
    """Restituisce un GeoDataFrame per uso locale"""
    return gpd.read_file(filepath).to_crs(epsg=4326)
