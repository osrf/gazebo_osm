import elementtree.ElementTree as Et
import xml.dom.minidom as minidom


class GetSDF:

    def __init__(self):
        self.sdf = Et.Element('sdf')
        self.sdf.set('version', "1.4")
        world = Et.SubElement(self.sdf, 'world')
        world.set('name', 'default')
        self.modelList = dict()

    def addSphericalCoords(self, latVal, lonVal, elevationVal=0.0, headingVal=0):
        ''' Add the spherical coordinates for the map'''
        spherical_coordinates = Et.SubElement(self.sdf.find('world'), 'spherical_coordinates')

        model = Et.SubElement(spherical_coordinates, 'surface_model')
        model.text = "EARTH_WGS84"

        lat = Et.SubElement(spherical_coordinates, 'latitude_deg')
        lat.text = str(latVal)

        lon = Et.SubElement(spherical_coordinates, 'longitude_deg')
        lon.text = str(lonVal)

        elevation = Et.SubElement(spherical_coordinates, 'elevation')
        elevation.text = str(elevationVal)

        heading = Et.SubElement(spherical_coordinates, 'heading_deg')
        heading.text = str(headingVal)

    def includeModel(self, modelName):
        ''' Include models in gazebo database'''
        includeModel = Et.SubElement(self.sdf.find('world'), 'include')
        includeUri = Et.SubElement(includeModel, 'uri')
        includeUri.text = "model://" + modelName
        return includeModel

    def addModel(self, mainModel, modelName, pose):
        '''Add model with pose and the name taken as inputs'''

        includeModel = self.includeModel(mainModel)

        model = Et.SubElement(includeModel, 'name')
        model.text = modelName

        static = Et.SubElement(includeModel, 'static')
        static.text = 'true'

        modelPose = Et.SubElement(includeModel, 'pose')
        modelPose.text = str(pose[0]) + " " + str(pose[1]) + " " + str(pose[2]) + " 0 0 0"

    def addRoad(self, roadName):
        '''Add road to sdf file'''
        road = Et.SubElement(self.sdf.find('world'), 'road')
        road.set('name', roadName)

    def setRoadWidth(self, width, roadName):
        ''' Set the width of the road specified by the road name'''
        allRoads = self.sdf.find('world').findall('road')

        roadWanted = [road for road in allRoads if road.get('name') == roadName]

        roadWidth = Et.SubElement(roadWanted[0], 'width')
        roadWidth.text = str(width)

    def addRoadPoint(self, point, roadName):
        '''Add points required to build a road, specified by the roadname'''
        allRoads = self.sdf.find('world').findall('road')
        roadWanted = [road for road in allRoads if road.get('name') == roadName]
        roadPoint = Et.SubElement(roadWanted[0], 'point')
        roadPoint.text = str(point[0]) + " " + str(point[1]) + " " + str(point[2])

    def writeToFile(self, filename):
        '''Write sdf file'''
        roughXml = Et.tostring(self.sdf, 'utf-8')
        reparsed = minidom.parseString(roughXml)
        prettyXml = reparsed.toprettyxml(indent="\t")
        outfile = open(filename, "w")
        outfile.write(prettyXml)
        outfile.close()


def test():
    p = GetSDF()
    p.addSphericalCoords(37.85, -122.5)
    p.addRoad("my_road")
    p.setRoadWidth(7.34, "my_road")
    p.addRoadPoint([0, 0, 0], "my_road")
    p.addRoadPoint([100, 0, 0], "my_road")
    p.addModel("stop_sign", "stop_sign_0", [1, 0, 1])
    p.writeToFile("outclass.sdf")
test()
