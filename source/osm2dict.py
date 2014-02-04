#!/usr/bin/env python
import numpy as np


class Osm2Dict:

    def __init__(self, lonStart, latStart, data):

        self.latStart = latStart
        self.lonStart = lonStart
        self.data = data
        #Radius of the Earth
        self.R = 6371

        #Dictionaries to store results
        self.records = dict()
        self.models = dict()

        self.highwayType = dict({"motorway": 4, "trunk": 3,
                                 "primary": 1.5, "secondary": 0.8,
                                 "tertiary": 0.42,
                                 "residential": 0.21})

        self.modelType = ['highway', 'amenity', 'building', 'emergency']

        self.addModel = dict({"stop": {"modelName": "stop_sign",
                                       "occurence": -1},
                              "street_lamp": {"modelName": "lamp_post",
                                              "occurence": -1},
                              "traffic_signals": {"modelName":
                                                  "construction_cone",
                                                  "occurence": -1},
                              "fire hydrant": {"modelName": "fire_hydrant",
                                               "occurence": -1}})

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
                                          'occurence': -1}})

    def latLonDist(self, coords):
        '''Input: latitude and longitude coordinates
           Returns the distance made by given coordinates with
           the starting coordinates'''
        if not coords:
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
        if not coords:
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
        if not coords:
            return []

        distance = self.latLonDist(coords)
        angles = self.latLongBearing(coords)

        point = np.array([distance*np.cos(angles)*1000,
                          distance*np.sin(angles)*1000,
                          np.zeros(np.shape(distance))*1000])

        return point

    def getMapDetails(self):
        ''' Returns a list of highways with corresponding widths
            and a list of all the models to be included'''

        # get the road latitude and longitudes
        for i in range(len(self.data)):
            tagData = self.data[i].get("data").get("tag")

            for modelNum in self.modelType:

                if tagData.get(modelNum) in self.addModel.keys():
                    modelType = tagData.get(modelNum)

                    coords = np.array([self.data[i].get("data").get("lon"),
                                       self.data[i].get("data").get("lat")])
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

                                if pointsXYZ:
                                    #Sort points in X, Y, Z
                                    index = np.lexsort((pointsXYZ[0, :],
                                                        pointsXYZ[1, :],
                                                        pointsXYZ[2, :]))

                                    location = pointsXYZ[:, index]

                                    self.records.update(dict({roadName:
                                                             {'points':
                                                              location,
                                                              'width':
                                                              self.highwayType
                                                              [typeHighway]}}))
                elif "building" in tagData:

                    if tagData.get("building") == "yes":
                        buildingName = tagData.get("name")

                        if "name_1" in tagData:
                                buildingName += tagData.get("name_1")

                        node_ref = self.data[i].get("data").get("nd")
                        coords = np.array([])

                        for j in range(len(self.data)):

                            if "node" in self.data[j].get("type"):

                                if (self.data[j].get("data").get("id")
                                   in node_ref):

                                    coords = np.append(coords,
                                                       self.data[j].get("data")
                                                                   .get("lon"))
                                    coords = np.append(coords,
                                                       self.data[j].get("data")
                                                                   .get("lat"))
                                    coords = np.reshape(coords,
                                                        (len(coords)/2, 2))

                        if coords.any() and buildingName is not None:
                            pointsXYZ = self.getPoints(coords)
                            if pointsXYZ:
                                #Sort points in X, Y, Z
                                index = np.lexsort((pointsXYZ[0, :],
                                                    pointsXYZ[1, :],
                                                    pointsXYZ[2, :]))

                                location = pointsXYZ[:, index]

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
                        coords = np.array([])

                        for j in range(len(self.data)):

                            if "node" in self.data[j].get("type"):

                                if (self.data[j].get("data").get("id")
                                   in node_ref):

                                    coords = np.append(coords,
                                                       self.data[j].get("data")
                                                                   .get("lon"))
                                    coords = np.append(coords,
                                                       self.data[j].get("data")
                                                                   .get("lat"))
                                    coords = np.reshape(coords,
                                                        (len(coords)/2, 2))

                        pointsXYZ = self.getPoints(coords)
                        if pointsXYZ:

                            #Sort points in X, Y, Z
                            index = np.lexsort((pointsXYZ[0, :],
                                                pointsXYZ[1, :],
                                                pointsXYZ[2, :]))

                            location = pointsXYZ[:, index]

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
        return self.records, self.models

    def getLat(self):
        '''Get the latitude of the start point'''
        return self.latStart

    def getLon(self):
        '''Get the longitude of the start point'''
        return self.lonStart
