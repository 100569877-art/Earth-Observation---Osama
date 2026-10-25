# LEVEL-1C

from l1c.src.initL1c import initL1c
from common.io.writeToa import writeToa, readToa
from common.io.readGeodetic import readGeodetic, getCorners
import mgrs
import numpy as np
from scipy.interpolate import bisplrep, bisplev
import matplotlib.pyplot as plt
from common.io.l1cProduct import writeL1c
from matplotlib import cm
import os


class l1c(initL1c):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def processModule(self):

        self.logger.info("Start of the L1C Processing Module")

        for band in self.globalConfig.bands:

            self.logger.info("Start of BAND " + band)

            # Read TOA - output of the L1B in Radiances
            # -------------------------------------------------------------------------------
            toa = readToa(
                self.l1bdir,
                self.globalConfig.l1b_toa + band + '.nc'
            )

            lat, lon = readGeodetic(
                self.gmdir,
                self.globalConfig.gm_geoloc
            )

            # Check consistency between geolocation and L1B dimensions
            self.checkSize(lat, toa)
            self.checkSize(lon, toa)

            # L1C reprojection onto the MGRS grid
            # -------------------------------------------------------------------------------
            lat_l1c, lon_l1c, toa_l1c = self.l1cProjtoa(
                lat,
                lon,
                toa,
                band
            )

            # Generate geometry plots only once
            # Geometry is common to the four radiometric bands
            # -------------------------------------------------------------------------------
            if band == self.globalConfig.bands[0]:

                self.plotGsd(
                    lat,
                    lon,
                    self.outdir
                )

                self.plotFootprint(
                    lat,
                    lon,
                    lat_l1c,
                    lon_l1c,
                    self.outdir
                )

            # Write output TOA
            # -------------------------------------------------------------------------------
            writeL1c(
                self.outdir,
                self.globalConfig.l1c_toa + band,
                lat_l1c,
                lon_l1c,
                toa_l1c
            )

            self.logger.info(
                "End of BAND " + band
            )

        self.logger.info(
            "End of the L1C Module!"
        )

    def l1cProjtoa(self, lat, lon, toa, band):
        '''
        This function reprojects the L1B radiances into the MGRS grid.

        The MGRS reference system:
        https://www.bluemarblegeo.com/knowledgebase/calculator-2020/
        Military_Grid_Reference_System_(MGRS).htm

        Example:
        MGRS: '31REQ4367374067'

        31 is the UTM zone.
        R is the UTM latitude band.
        EQ are the MGRS column and row band letters.
        43673 is the MGRS Easting.
        74067 is the MGRS Northing.

        Python mgrs library:
        https://pypi.org/project/mgrs/

        :param lat: L1B latitudes [deg]
        :param lon: L1B longitudes [deg]
        :param toa: L1B radiances
        :param band: band
        :return: L1C latitude, longitude and radiances
        '''

        # -------------------------------------------------------------------------------
        # Interpolation function using L1B geolocation and radiance
        # -------------------------------------------------------------------------------
        tck = bisplrep(
            lat.flatten(),
            lon.flatten(),
            toa.flatten()
        )

        # MGRS converter
        m = mgrs.MGRS()

        # -------------------------------------------------------------------------------
        # Generate unique MGRS cells covered by the L1B image
        # -------------------------------------------------------------------------------
        mgrs_tiles = set()

        for ialt in range(lat.shape[0]):

            for iact in range(lat.shape[1]):

                tile = m.toMGRS(
                    lat[ialt, iact],
                    lon[ialt, iact],
                    MGRSPrecision=self.l1cConfig.mgrs_tile_precision
                )

                if isinstance(tile, bytes):
                    tile = tile.decode('utf-8')

                mgrs_tiles.add(tile)

        # Deterministic output ordering
        mgrs_tiles = sorted(mgrs_tiles)

        npoints = len(mgrs_tiles)

        self.logger.debug(
            'Number of L1C MGRS grid points: '
            + str(npoints)
        )

        # -------------------------------------------------------------------------------
        # Allocate output arrays
        # -------------------------------------------------------------------------------
        lat_l1c = np.zeros(npoints)
        lon_l1c = np.zeros(npoints)
        toa_l1c = np.zeros(npoints)

        # -------------------------------------------------------------------------------
        # Convert MGRS cells back to latitude/longitude and interpolate radiance
        # -------------------------------------------------------------------------------
        for i, tile in enumerate(mgrs_tiles):

            lat_l1c[i], lon_l1c[i] = m.toLatLon(
                tile
            )

            toa_l1c[i] = bisplev(
                lat_l1c[i],
                lon_l1c[i],
                tck
            )

        return lat_l1c, lon_l1c, toa_l1c

    def checkSize(self, lat, toa):
        '''
        Check the sizes of the input radiances and geodetic coordinates.
        If they do not match, exit.

        :param lat: Latitude or longitude 2D matrix
        :param toa: Radiance 2D matrix
        :return: NA
        '''

        if lat.shape != toa.shape:

            raise ValueError(
                'L1B TOA and geolocation matrices have different sizes: '
                + str(toa.shape)
                + ' != '
                + str(lat.shape)
            )

    def distanceGround(self, lat1, lon1, lat2, lon2):
        '''
        Ground distance between two geographic coordinates
        using the haversine formula.

        :return: distance in metres
        '''

        R = 6371000.0

        lat1 = np.radians(lat1)
        lon1 = np.radians(lon1)
        lat2 = np.radians(lat2)
        lon2 = np.radians(lon2)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            np.sin(dlat / 2.0) ** 2
            + np.cos(lat1)
            * np.cos(lat2)
            * np.sin(dlon / 2.0) ** 2
        )

        c = 2.0 * np.arctan2(
            np.sqrt(a),
            np.sqrt(1.0 - a)
        )

        return R * c

    def plotGsd(self, lat, lon, outputdir):
        '''
        Plot L1B and L1C Ground Sampling Distance
        in across-track and along-track directions.
        '''

        # -------------------------------------------------------------------------------
        # L1B ACT GSD
        # Central ALT row
        # -------------------------------------------------------------------------------
        idalt = int(
            lat.shape[0] / 2
        )

        gsd_act_l1b = np.zeros(
            lat.shape[1] - 1
        )

        for iact in range(
                lat.shape[1] - 1):

            gsd_act_l1b[iact] = self.distanceGround(
                lat[idalt, iact],
                lon[idalt, iact],
                lat[idalt, iact + 1],
                lon[idalt, iact + 1]
            )

        # -------------------------------------------------------------------------------
        # L1B ALT GSD
        # Central ACT column
        # -------------------------------------------------------------------------------
        idact = int(
            lat.shape[1] / 2
        )

        gsd_alt_l1b = np.zeros(
            lat.shape[0] - 1
        )

        for ialt in range(
                lat.shape[0] - 1):

            gsd_alt_l1b[ialt] = self.distanceGround(
                lat[ialt, idact],
                lon[ialt, idact],
                lat[ialt + 1, idact],
                lon[ialt + 1, idact]
            )

        # -------------------------------------------------------------------------------
        # L1C grid
        # MGRS precision = 3 corresponds to 100 m
        # -------------------------------------------------------------------------------
        gsd_act_l1c = np.ones(
            len(gsd_act_l1b)
        ) * 100.0

        gsd_alt_l1c = np.ones(
            len(gsd_alt_l1b)
        ) * 100.0

        # -------------------------------------------------------------------------------
        # ACT plot
        # -------------------------------------------------------------------------------
        plt.figure()

        plt.plot(
            gsd_act_l1b,
            label='L1B'
        )

        plt.plot(
            gsd_act_l1c,
            label='L1C'
        )

        plt.xlabel(
            'ACT pixel [-]'
        )

        plt.ylabel(
            'GSD [m]'
        )

        plt.title(
            'GSD comparison - Across Track'
        )

        plt.grid()
        plt.legend()

        filename_act = os.path.join(
            outputdir,
            'l1c_gsd_act.png'
        )

        plt.savefig(
            filename_act,
            dpi=200
        )

        plt.close()

        # -------------------------------------------------------------------------------
        # ALT plot
        # -------------------------------------------------------------------------------
        plt.figure()

        plt.plot(
            gsd_alt_l1b,
            label='L1B'
        )

        plt.plot(
            gsd_alt_l1c,
            label='L1C'
        )

        plt.xlabel(
            'ALT pixel [-]'
        )

        plt.ylabel(
            'GSD [m]'
        )

        plt.title(
            'GSD comparison - Along Track'
        )

        plt.grid()
        plt.legend()

        filename_alt = os.path.join(
            outputdir,
            'l1c_gsd_alt.png'
        )

        plt.savefig(
            filename_alt,
            dpi=200
        )

        plt.close()

    def plotFootprint(
            self,
            lat,
            lon,
            lat_l1c,
            lon_l1c,
            outputdir):
        '''
        Plot the L1B ground footprint together
        with the L1C MGRS grid points.
        '''

        lat_corners = getCorners(
            lat
        )

        lon_corners = getCorners(
            lon
        )

        plt.figure()

        # L1C MGRS grid points
        plt.scatter(
            lon_l1c,
            lat_l1c,
            s=4,
            label='L1C MGRS grid'
        )

        # L1B footprint
        plt.plot(
            lon_corners,
            lat_corners,
            linewidth=2,
            label='L1B footprint'
        )

        plt.xlabel(
            'Longitude [deg]'
        )

        plt.ylabel(
            'Latitude [deg]'
        )

        plt.title(
            'L1B footprint and L1C MGRS grid'
        )

        plt.grid()
        plt.legend()

        filename = os.path.join(
            outputdir,
            'l1c_footprint.png'
        )

        plt.savefig(
            filename,
            dpi=200
        )

        plt.close()