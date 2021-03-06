"""
Copyright 2016 Open Networking Foundation ( ONF )

Please refer questions to either the onos test mailing list at <onos-test@onosproject.org>,
the System Testing Plans and Results wiki page at <https://wiki.onosproject.org/x/voMg>,
or the System Testing Guide page at <https://wiki.onosproject.org/x/WYQg>

    TestON is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    ( at your option ) any later version.

    TestON is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TestON.  If not, see <http://www.gnu.org/licenses/>.
"""
"""
Graph algorithm implementations for CHOTestMonkey
Author: you@onlab.us
"""
class GraphHelper:

    """
    This class implements graph algorithms for CHOTestMonkey.
    It reads main.devices and main.links as vertices and edges.
    Currently it offers functions for finding ( non- )cut-edges and vertices,
    which is realized based on chain-decomposition algorithm
    """
    def __init__( self ):
        # Depth-first index of each node
        self.DFI = []
        # Parent vertex and egde of each node in depth-first search tree
        self.parentDeviceInDFS = []
        self.parentLinkInDFS = []
        # Data structures for chain-decomposition algorithm
        self.backEdges = {}
        self.chains = []
        self.currentDFI = 0
        self.upDevices = []
        for device in main.devices:
            if device.isUp():
                self.upDevices.append( device )
        for i in range( len( main.devices ) ):
            self.DFI.append( -1 )
            self.parentDeviceInDFS.append( None )
            self.parentLinkInDFS.append( None )

    def genDFIandBackEdge( self, device ):
        """
        This function runs a depth-first search and get DFI of each node
        as well as collect the back edges
        """
        self.DFI[ device.index ] = self.currentDFI
        self.currentDFI += 1
        for link in device.outgoingLinks:
            if not link.isUp():
                continue
            backwardLink = link.backwardLink
            neighbor = link.deviceB
            if neighbor == self.parentDeviceInDFS[ device.index ]:
                continue
            elif self.DFI[ neighbor.index ] == -1:
                self.parentDeviceInDFS[ neighbor.index ] = device
                self.parentLinkInDFS[ neighbor.index ] = backwardLink
                self.genDFIandBackEdge( neighbor )
            else:
                key = self.DFI[ neighbor.index ]
                if key in self.backEdges.keys():
                    if link not in self.backEdges[ key ] and\
                            backwardLink not in self.backEdges[ key ]:
                        self.backEdges[ key ].append( backwardLink )
                else:
                    tempKey = self.DFI[ device.index ]
                    if tempKey in self.backEdges.keys():
                        if link not in self.backEdges[ tempKey ] and\
                                backwardLink not in self.backEdges[ tempKey ]:
                            self.backEdges[ key ] = [ backwardLink ]
                    else:
                        self.backEdges[ key ] = [ backwardLink ]

    def findChains( self ):
        """
        This function finds all the 'chains' for chain-decomposition algorithm
        """
        keyList = sorted( self.backEdges.keys() )
        deviceIsVisited = []
        for i in range( len( main.devices ) ):
            deviceIsVisited.append( 0 )
        for key in keyList:
            backEdgeList = self.backEdges[ key ]
            for link in backEdgeList:
                chain = []
                currentLink = link
                sourceDevice = link.deviceA
                while True:
                    currentDevice = currentLink.deviceA
                    nextDevice = currentLink.deviceB
                    deviceIsVisited[ currentDevice.index ] = 1
                    chain.append( currentLink )
                    if nextDevice == sourceDevice or deviceIsVisited[ nextDevice.index ] == 1:
                        break
                    currentLink = self.parentLinkInDFS[ nextDevice.index ]
                self.chains.append( chain )

    def getNonCutEdges( self ):
        """
        This function returns all non-cut-edges of a graph
        """
        assert len( self.upDevices ) != 0
        self.genDFIandBackEdge( self.upDevices[ 0 ] )
        self.findChains()
        nonCutEdges = []
        for chain in self.chains:
            for link in chain:
                nonCutEdges.append( link )
        return nonCutEdges

    def getNonCutVertices( self ):
        """
        This function returns all non-cut-vertices of a graph
        """
        nonCutEdges = self.getNonCutEdges()
        nonCutVertices = []
        for device in self.upDevices:
            deviceIsNonCut = True
            for link in device.outgoingLinks:
                if link.isUp() and not ( link in nonCutEdges or link.backwardLink in nonCutEdges ):
                    deviceIsNonCut = False
                    break
            if deviceIsNonCut:
                nonCutVertices.append( device )
        return nonCutVertices

    def printDFI( self ):
        print self.DFI

    def printParentInDFS( self ):
        print self.parentInDFS

    def printBackEdges( self ):
        print self.backEdges

    def printChains( self ):
        chainIndex = 0
        for chain in self.chains:
            print chainIndex
            for link in chain:
                print link
            chainIndex += 1
