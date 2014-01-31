import urllib2
import osmapi


def getOsmFile(box, filename = 'map.osm'):

    osmFile = urllib2.urlopen('http://api.openstreetmap.org/api/0.6/map?bbox='
                              + str(box)[1:-1].replace(" ", ""))

    osm = open('map.osm','w')

    osm.write(osmFile.read())

    osm.close()

    osmRead = open('map.osm', 'r')

    myapi = osmapi.OsmApi()

    dataDict = myapi.ParseOsm(osmRead.read())

    osmRead.close()

    return dataDict
