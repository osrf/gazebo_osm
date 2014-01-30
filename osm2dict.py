#!/usr/bin/env python
import osmapi
import numpy as np
from getMapImage import getMapImage


class Osm2Dict:

    def __init__(self):
        self.R = 6371
        self.records = dict()

        self.models = dict()
        self.highwayWidthRelation = dict({"motorway": 4, "trunk": 3,
                                         "primary": 1.5, "secondary": 0.8,
                                         "tertiary": 0.42, "residential": 0.21})

        self.modelType = ['highway', 'amenity', 'building', 'emergency']

        self.addModel = dict({"stop": {"modelName": "stop_sign", "occurence": -1},
                              "street_lamp": {"modelName": "lamp_post", "occurence": -1},
                              "traffic_signals": {"modelName": "construction_cone", "occurence": -1},
                              "fire hydrant": {"modelName": "fire_hydrant", "occurence": -1}})

        self.amenityList = dict({"school": {"modelName": "house_1", "occurence": -1},
                                 "post_office": {'modelName': "office_building", 'occurence': -1},
                                 "university": {'modelName': "house_2", 'occurence': -1},
                                 "library": {'modelName': "house_2", 'occurence': -1},
                                 "bar": {'modelName': "house_3", 'occurence': -1},
                                 "cafe": {'modelName': "house_3", 'occurence': -1},
                                 "pub": {'modelName': "house_3", 'occurence': -1},
                                 "restaurant": {'modelName': "house_3", 'occurence': -1},
                                 "fast_food": {'modelName': "house_3", 'occurence': -1},
                                 "college": {'modelName': "house_2", 'occurence': -1},
                                 "kindergarten": {'modelName': "house_2", 'occurence': -1},
                                 "fuel": {'modelName': "gas_station", 'occurence': -1}})

        while 1:
            #get map coords
            print("\nPlease enter the latitudnal and logitudnal" +
                  "coordinates of the area or select from default by hitting return twice \n")

            startCoords = raw_input("Enter starting coordinates: [lon lat] :").split(' ')
            endCoords = raw_input("Enter ending coordnates: [lon lat]: ").split(' ')

            if startCoords != [] and endCoords != [] and len(startCoords) == 2 and len(endCoords) == 2:

                for incoords in range(2):

                    startCoords[incoords] = float(startCoords[incoords])
                    endCoords[incoords] = float(endCoords[incoords])

            else:

                choice = raw_input("Default Coordinate options: West El" +
                                   "Camino Highway, CA (default), Bethlehem, PA (2): ")

                if choice == '2':
                    startCoords, endCoords = [40.61, -75.382], [40.608, -75.3714]

                else:
                    startCoords, endCoords = [37.385844, -122.101464], [37.395664, -122.083697]

            option = raw_input("Do you want to view the area specified? [Y/N] (default: Y) ").upper()

            if option == 'N':
                break

            getMapImage([min(startCoords[1], endCoords[1]),
                         min(startCoords[0], endCoords[0]),
                         max(startCoords[1], endCoords[1]),
                         max(startCoords[0], endCoords[0])])

            final_choice = raw_input("Do you want to continue (C) or select new coordinates (S)? (default:C)").upper()

            if final_choice == 'S':
                continue

            break

        self.latStart = startCoords[0]
        self.lonStart = startCoords[1]
        self.latStop = endCoords[0]
        self.lonStop = endCoords[1]

    def latLonDist(self, coords):
        '''Input: latitude and longitude coordinates
           Returns the distance made by given coordinates with
           the starting coordinates'''
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
        angle = np.array([])
        for i in range(len(coords)):

            lon2 = np.radians(coords[i][0])
            lat2 = np.radians(coords[i][1])

            dLat = lat2-np.radians(self.latStart)
            dLon = lon2-np.radians(self.lonStart)

            angle = np.append(angle, (np.arctan2(np.sin(dLon) * np.cos(lat2),
                                      np.cos(np.radians(self.latStart)) *
                                      np.sin(lat2) - np.sin(np.radians(self.latStart)) *
                                      np.cos(lat2) * np.cos(dLon))))
        return angle

    def getPoints(self, coords):
        '''Input : latitude and longitudnal coordinates
           Return the points in gazebo frame '''
        distance = self.latLonDist(coords)
        angles = self.latLongBearing(coords)

        point = np.array([distance*np.cos(angles)*1000,
                          distance*np.sin(angles)*1000,
                          np.zeros(np.shape(distance))*1000])

        return point

    def getMapDetails(self):
        ''' Returns a list of highways with corresponding widhts and a list of all the models to be included'''
        #initialize the Open street api
        MyApi = osmapi.OsmApi()
        #Get the map data reqd
        data = MyApi.Map(min(self.lonStart, self.lonStop),
                         min(self.latStart, self.latStop),
                         max(self.lonStart, self.lonStop),
                         max(self.latStart, self.latStop))

        # get the road latitude and longitudes
        for i in range(len(data)):
            tagData = data[i].get("data").get("tag")

            for modelNum in self.modelType:

                if tagData.get(modelNum) in self.addModel.keys():
                    modelType = tagData.get(modelNum)

                    coords = np.array([data[i].get("data").get("lon"), data[i].get("data").get("lat")])
                    coords = np.reshape(coords, (len(coords)/2, 2))
                    modelLocation = self.getPoints(coords)

                    self.addModel[modelType]['occurence'] += 1
                    repNum = self.addModel[modelType]['occurence']
                    self.models.update(dict({self.addModel[modelType]['modelName'] + "_" + str(repNum):
                                            {"points": modelLocation,
                                             "mainModel": self.addModel[modelType]['modelName']}}))

            if "way" in data[i].get("type"):
                if "highway" in tagData:
                    highwayType = tagData.get("highway")

                    if highwayType in self.highwayWidthRelation.keys():

                                roadName = tagData.get("name")

                                if roadName is None:
                                    roadName = highwayType + "_" + str(data[i].get("data").get("id"))
                                else:
                                    roadName += "_" + str(data[i].get("data").get("id"))

                                node_ref = data[i].get("data").get("nd")
                                coords = np.array([])

                                for j in range(len(data)):

                                    if "node" in data[j].get("type"):

                                        if data[j].get("data").get("id") in node_ref:
                                            coords = np.append(coords, data[j].get("data").get("lon"))
                                            coords = np.append(coords, data[j].get("data").get("lat"))
                                            coords = np.reshape(coords, (len(coords)/2, 2))

                                pointsXYZ = self.getPoints(coords)

                                #Sort points in X, Y, Z
                                index = np.lexsort((pointsXYZ[0, :], pointsXYZ[1, :], pointsXYZ[2, :]))
                                orderedPoints = pointsXYZ[:, index]

                                self.records.update(dict({roadName: {'points': orderedPoints,
                                                                     'width': self.highwayWidthRelation[highwayType]}}))
                elif "building" in tagData:

                    if tagData.get("building") == "yes":
                        buildingName = tagData.get("name")

                        if "name_1" in tagData:
                                buildingName += tagData.get("name_1")

                        node_ref = data[i].get("data").get("nd")
                        coords = np.array([])

                        for j in range(len(data)):

                                    if "node" in data[j].get("type"):

                                        if data[j].get("data").get("id") in node_ref:

                                            coords = np.append(coords, data[j].get("data").get("lon"))
                                            coords = np.append(coords, data[j].get("data").get("lat"))
                                            coords = np.reshape(coords, (len(coords)/2, 2))

                        if coords != [] and buildingName is not None:

                            pointsXYZ = self.getPoints(coords)
                            #Sort points in X, Y, Z
                            index = np.lexsort((pointsXYZ[0, :], pointsXYZ[1, :], pointsXYZ[2, :]))
                            orderedPoints = pointsXYZ[:, index]

                            buildingLocation = np.array([[sum(orderedPoints[0, :])/len(orderedPoints[0, :])],
                                                         [sum(orderedPoints[1, :])/len(orderedPoints[1, :])],
                                                         [sum(orderedPoints[2, :])/len(orderedPoints[2, :])]])

                            self.models.update(dict({buildingName: {"points": buildingLocation,
                                                                    "mainModel": "office_building"}}))

                elif "amenity" in tagData:
                    if tagData.get("amenity") in self.amenityList.keys():

                        amenityName = tagData.get("amenity")

                        node_ref = data[i].get("data").get("nd")
                        coords = np.array([])

                        for j in range(len(data)):

                            if "node" in data[j].get("type"):

                                if data[j].get("data").get("id") in node_ref:

                                    coords = np.append(coords, data[j].get("data").get("lon"))
                                    coords = np.append(coords, data[j].get("data").get("lat"))
                                    coords = np.reshape(coords, (len(coords)/2, 2))

                        pointsXYZ = self.getPoints(coords)

                        #Sort points in X, Y, Z
                        index = np.lexsort((pointsXYZ[0, :], pointsXYZ[1, :], pointsXYZ[2, :]))
                        orderedPoints = pointsXYZ[:, index]

                        amenityLocation = np.array([[sum(orderedPoints[0, :])/len(orderedPoints[0, :])],
                                                    [sum(orderedPoints[1, :])/len(orderedPoints[1, :])],
                                                    [sum(orderedPoints[2, :])/len(orderedPoints[2, :])]])

                        self.amenityList[amenityName]['occurence'] += 1
                        repNum = self.amenityList[amenityName]['occurence']

                        self.models.update(dict({amenityName + "_" + str(repNum):
                                                {"points": amenityLocation,
                                                 "mainModel": self.amenityList[amenityName]['modelName']}}))
        return self.records, self.models

    def getLat(self):
        '''Get the latitude of the start point'''
        return self.latStart

    def getLon(self):
        '''Get the longitude of the start point'''
        return self.lonStart
