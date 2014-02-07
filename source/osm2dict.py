#!/usr/bin/env python
import numpy as np


class Osm2Dict:

    def __init__(self, lonStart, latStart, data, flags=['a']):

        self.latStart = latStart
        self.lonStart = lonStart
        self.data = data
        self.displayAll = 'a' in flags
        self.displayModels = 'm' in flags
        self.displayRoads = 'r' in flags
        self.flags = flags
        #Radius of the Earth
        self.R = 6371

        #Dictionaries to store results
        self.records = dict()
        self.models = dict()

        self.highwayType = dict({"footway": 0.5, "cycleway": 0.5,
                                 "path": 0.5, "pedestrian": 0.5,
                                 "motorway": 14, "motorway_link": 13,
                                 "trunk": 12, "trunk_link": 11,
                                 "primary": 10, "primary_link": 9,
                                 "secondary": 8, "secondary_link": 7,
                                 "tertiary": 6, "tertiary_link": 5,
                                 "residential": 4, "linving_street": 4,
                                 "road": 5, "steps": 0.8})

        self.modelType = ['highway', 'amenity', 'building', 'emergency']

        self.addModel = dict({"stop": {"modelName": "stop_sign",
                                       "occurence": -1},
                              "street_lamp": {"modelName": "lamp_post",
                                              "occurence": -1},
                              "traffic_signals": {"modelName":
                                                  "construction_cone",
                                                  "occurence": -1},
                              "fire hydrant": {"modelName": "fire_hydrant",
                                               "occurence": -1},
                              "steps": {"modelName": "nist_stairs_120",
                                        "occurence": -1},
                              "give_way": {"modelName": "speed_limit",
                                           "occurence": -1},
                              "bus_stop": {"modelName":
                                           "robocup14_spl_goal",
                                           "occurence": -1}
                              })

        self.amenityList = dict({"school": {"modelName": "house_1",
                                            "occurence": -1},
                                 "post_office": {'modelName':
                                                 "office_building",
                                                 'occurence': -1},
                                 "university": {'modelName': "house_2",
                                                'occurence': -1},
                                 "library": {'modelName': "house_2",
                                             'occurence': -1},
                                 "bar": {'modelName': "house_3",
                                         'occurence': -1},
                                 "cafe": {'modelName': "house_3",
                                          'occurence': -1},
                                 "pub": {'modelName': "house_3",
                                         'occurence': -1},
                                 "restaurant": {'modelName': "house_3",
                                                'occurence': -1},
                                 "fast_food": {'modelName': "house_3",
                                               'occurence': -1},
                                 "college": {'modelName': "house_2",
                                             'occurence': -1},
                                 "kindergarten": {'modelName': "house_2",
                                                  'occurence': -1},
                                 "fuel": {'modelName': "gas_station",
                                          'occurence': -1},
                                 "parking": {'modelName':
                                             "drc_practice_angled_barrier_45",
                                             'occurence': -1}
                                 })

    def latLonDist(self, coords):
        '''Input: latitude and longitude coordinates
           Returns the distance made by given coordinates with
           the starting coordinates'''
        if not coords.any():
            return 0

        distance = np.array([])

        for cordinate in range(len(coords)):

            lon2 = np.radians(coords[cordinate][0])
            lat2 = np.radians(coords[cordinate][1])

            dLat = lat2-np.radians(self.latStart)
            dLon = lon2-np.radians(self.lonStart)

            a = (np.sin(dLat/2) * np.sin(dLat/2) +
                 np.sin(dLon/2) * np.sin(dLon/2) *
                 np.cos(np.radians(self.latStart)) *
                 np.cos(lat2))

            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))

            distance = np.append(distance, self.R * c)

        return distance

    def latLongBearing(self, coords):
        '''Input: latitude and longitude coordinates
           Return the angle made by given coordinates with
           the starting coordinates'''
        if not coords.any():
            return 0

        angle = np.array([])
        for i in range(len(coords)):

            lon2 = np.radians(coords[i][0])
            lat2 = np.radians(coords[i][1])

            dLat = lat2-np.radians(self.latStart)
            dLon = lon2-np.radians(self.lonStart)

            angle = np.append(angle, (np.arctan2(np.sin(dLon) * np.cos(lat2),
                                      np.cos(np.radians(self.latStart)) *
                                      np.sin(lat2) -
                                      np.sin(np.radians(self.latStart)) *
                                      np.cos(lat2) * np.cos(dLon))))
        return angle

    def getPoints(self, coords):
        '''Input : latitude and longitudnal coordinates
           Return the points in gazebo frame '''
        if not coords.any():
            return []

        distance = self.latLonDist(coords)
        angles = self.latLongBearing(coords)

        point = np.array([distance*np.cos(angles) * 1000,
                          -distance*np.sin(angles) * 1000,
                          np.zeros(np.shape(distance))*1000])

        return point

    def latLonToPoints(self, node_ref):

        coords = np.array([])
        for j in range(len(self.data)):

            if "node" in self.data[j].get("type"):

                if ((self.data[j].get("data")
                                 .get("id"))
                   in node_ref):

                    coords = np.append(coords,
                                       self.data[j]
                                       .get("data")
                                       .get("lon"))
                    coords = np.append(coords,
                                       self.data[j]
                                       .get("data")
                                       .get("lat"))
                    coords = np.reshape(coords,
                                        (len(coords)/2,
                                         2))

        pointsXYZ = self.getPoints(coords)

        if pointsXYZ.any():
            pointsXYZ.sort(axis=1)

        return pointsXYZ

    def getRoadDetails(self):
        '''Returns a list of roads with corresponding widths'''
         # get the road latitude and longitudes
        for i in range(len(self.data)):
            tagData = self.data[i].get("data").get("tag")
            if "way" in self.data[i].get("type"):
                if "highway" in tagData:
                    typeHighway = tagData.get("highway")

                    if typeHighway in self.highwayType.keys():

                                roadName = tagData.get("name")

                                if roadName is None:
                                    roadName = (typeHighway +
                                                "_" +
                                                str(self.data[i].get("data")
                                                                .get("id")))
                                else:
                                    roadName += "_" + str(self.data[i]
                                                              .get("data")
                                                              .get("id"))

                                node_ref = self.data[i].get("data").get("nd")
                                if node_ref:
                                    location = self.latLonToPoints(node_ref)

                                    self.records.update(dict({roadName:
                                                             {'points':
                                                              location,
                                                              'width':
                                                              self.highwayType
                                                              [typeHighway]}}))
        return self.records

    def getModelDetails(self):
        '''Returns a list of models like buildings to be included
            in the map'''
        for i in range(len(self.data)):
            tagData = self.data[i].get("data").get("tag")

            for modelNum in self.modelType:

                if tagData.get(modelNum) in self.addModel.keys():
                    modelType = tagData.get(modelNum)

                    if modelType == 'steps':
                        node_ref = self.data[i].get("data").get("nd")

                        for j in range(len(self.data)):

                            if "node" in self.data[j].get("type"):

                                if ((self.data[j].get("data")
                                                 .get("id"))
                                   in node_ref):

                                    coords = np.append(coords,
                                                       self.data[j]
                                                       .get("data")
                                                       .get("lon"))
                                    coords = np.append(coords,
                                                       self.data[j]
                                                       .get("data")
                                                       .get("lat"))
                    else:
                        coords = np.array([self.data[i].get("data")
                                                       .get("lon"),
                                           self.data[i].get("data")
                                                       .get("lat")])
                    coords = np.reshape(coords, (len(coords)/2, 2))

                    modelLocation = self.getPoints(coords)

                    self.addModel[modelType]['occurence'] += 1

                    repNum = self.addModel[modelType]['occurence']

                    self.models.update(dict({self.addModel
                                             [modelType]['modelName'] +
                                             "_" + str(repNum):
                                            {"points": modelLocation,
                                             "mainModel": self.addModel
                                             [modelType]['modelName']}}))
            if "building" in tagData:

                if tagData.get("building") == "yes":
                    if "name" in tagData:
                        buildingName = tagData.get("name")
                    else:
                        buildingName = ("office_building" +
                                        "_" +
                                        str(self.data[i].get("data")
                                                        .get("id")))
                    if "name_1" in tagData:
                        buildingName += tagData.get("name_1")

                    node_ref = self.data[i].get("data").get("nd")

                    if node_ref:
                        location = self.latLonToPoints(node_ref)

                        buildingLoc = np.array([[sum(location[0, :]) /
                                                 len(location[0, :])],
                                                [sum(location[1, :]) /
                                                 len(location[1, :])],
                                                [sum(location[2, :]) /
                                                 len(location[2, :])]]
                                               )

                        self.models.update(dict({buildingName:
                                                {"points":
                                                 buildingLoc,
                                                 "mainModel":
                                                 "office_building"}}))

            elif "amenity" in tagData:
                if tagData.get("amenity") in self.amenityList.keys():

                    amenity = tagData.get("amenity")

                    node_ref = self.data[i].get("data").get("nd")
                    if node_ref:
                        location = self.latLonToPoints(node_ref)

                        amenityLocation = np.array([[sum(location[0, :]) /
                                                     len(location[0, :])],
                                                    [sum(location[1, :]) /
                                                     len(location[1, :])],
                                                    [sum(location[2, :]) /
                                                     len(location[2, :])]]
                                                   )

                        self.amenityList[amenity]['occurence'] += 1
                        repNum = self.amenityList[amenity]['occurence']

                        self.models.update(dict({amenity +
                                                 "_" + str(repNum):
                                                {"points": amenityLocation,
                                                 "mainModel":
                                                 self.amenityList
                                                 [amenity]
                                                 ['modelName']
                                                 }}))

    def getMapDetails(self):
        ''' Returns a list of highways with corresponding widths
            and a list of all the models to be included'''
        if self.displayAll or self.displayModels:
            self.getModelDetails()
        if self.displayAll or self.displayRoads:
            self.getRoadDetails()
        return self.records, self.models

    def setFlags(self, addFlag):

        if addFlag in ['a', 'm', 'r']:

            if addFlag == 'a':
                self.displayAll = True

            if addFlag == 'm':
                self.displayModels = True
                self.displayAll = False

            if addFlag == 'r':
                self.displayRoads = True
                self.displayAll = False

            return True
        else:

            print 'Error: Invalid flag! [Valid values : "a", "m", "r"]'
            return False

    def getFlags(self):
        flags = []

        if self.displayRoads:
            flags.append('r')

        if self.displayAll:
            flags.append('a')

        if self.displayModels:
            flags.append('m')

        return flags

    def getLat(self):
        '''Get the latitude of the start point'''
        return self.latStart

    def getLon(self):
        '''Get the longitude of the start point'''
        return self.lonStart
