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
        # Generate the unique MGRS cells covered by the L1B image
        # -------------------------------------------------------------------------------
        mgrs_tiles = set()

        for ialt in range(lat.shape[0]):

            for iact in range(lat.shape[1]):

                tile = m.toMGRS(
                    lat[ialt, iact],
                    lon[ialt, iact],
                    MGRSPrecision=self.l1cConfig.mgrs_tile_precision
                )

                # mgrs library may return bytes
                if isinstance(tile, bytes):
                    tile = tile.decode('utf-8')

                mgrs_tiles.add(tile)

        # Sort tiles so output order is deterministic
        mgrs_tiles = sorted(mgrs_tiles)

        npoints = len(mgrs_tiles)

        self.logger.debug(
            'Number of L1C MGRS grid points: '
            + str(npoints)
        )

        # -------------------------------------------------------------------------------
        # Allocate L1C arrays
        # -------------------------------------------------------------------------------
        lat_l1c = np.zeros(npoints)
        lon_l1c = np.zeros(npoints)
        toa_l1c = np.zeros(npoints)

        # -------------------------------------------------------------------------------
        # Convert each MGRS tile back to latitude/longitude and interpolate radiance
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
        If they don't match, exit.

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