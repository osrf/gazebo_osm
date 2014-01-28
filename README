This folder contains files for building osm_plugin for gazebo simulator.

Dependencies:
	Python 2.x
	Python packages: elementtree, osmapi
	(installation: pip install elementtree osmapi)
	Mapnik:
	sudo apt-get install -y python-software-properties
        sudo add-apt-repository ppa:mapnik/v2.2.0
	sudo apt-get update
	sudo apt-get install libmapnik libmapnik-dev mapnik-utils python-mapnik
Files:
osm2dict.py
	Collects data about certain types of roads based on input coordinates from osm database and converts the information received to format that can be used to build sdf files.

dict2sdf.py
	Usd to build sdf file from data received about the elements in the sdf format. 
	functionality:
		add models to world
		add road element
		set road width
		add points to the road element

example.py
	A test file which outputs a sdf file ( set to "outFile.sdf" in example.py).

Usage:
	Run example.py file
		python example.py
	Output file: outFile.sdf

	Check the file on gazebo
		gazebo outFile.sdf

