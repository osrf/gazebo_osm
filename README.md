# OSM Plug-in for Gazebo/Stage #
	
	Author:         Tashwin Khurana
	Maintainer:     Krystian Gebis
	Version:        1.9
	Description:    Open Street Maps plugin for Gazebo and Stage Simulators
	                This folder contains files for building osm_plugin for both simulators.
	

## Dependencies: ##

	Python 2.7
	OpenCV
	Mapnik:
		https://github.com/mapnik/mapnik/wiki/UbuntuInstallation


## Files: ##

***osm2dict.py***

Collects data about certain types of roads based on input coordinates from osm database and converts the information received to format that can be used to build sdf files.

***dict2sdf.py***

Used to build sdf file from data received about the elements in the sdf format. 
 - functionality: 
  - add models to world, 
  - add road element, 
  - set road width, 
  - add points to the road element

***getMapImage.py***

Gets the image of the area required to be simulated.
       
***getOsmFile.py***

Downloads the osm database of the specified area.

***gz_osm.py***

 Command line compatible program which combine the functionality of all the above classes and functions to output the .sdf file for gazebo. 

	usage: gz_osm.py [-h] [-f OUTFILE] [-o OSMFILE] [-O INPUTOSMFILE]
	                 [-i IMAGEFILE] [-d DIRECTORY]
	                 [-B [BOUNDINGBOX [BOUNDINGBOX ...]]] [-r] [-m] [-b] [-a]
	                 [--interactive]
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -f OUTFILE, --outFile OUTFILE
	                        Output file name
	  -o OSMFILE, --osmFile OSMFILE
	                        Name of the osm file generated
	  -O INPUTOSMFILE, --inputOsmFile INPUTOSMFILE
	                        Name of the Input osm file
	  -i IMAGEFILE, --imageFile IMAGEFILE
	                        Generate and name .png image of the selected areas
	  -d DIRECTORY, --directory DIRECTORY
	                        Output directory
	  -B [BOUNDINGBOX [BOUNDINGBOX ...]], --boundingbox [BOUNDINGBOX [BOUNDINGBOX ...]]
	                        Give the bounding box for the area Format: MinLon
	                        MinLat MaxLon MaxLat
	  -r, --roads           Display Roads
	  -m, --models          Display models
	  -b, --buildings       Display buildings
	  -a, --displayAll      Display roads and models
	  --interactive         Starts the interactive version of the program



## Example Usage: ##

Generate World from manually exported .osm file:
	
	` ./gz_osm.py -O map.osm`
	
	Output file: outFile.sdf (default)

	Check the file on gazebo
		gazebo outFile.sdf
