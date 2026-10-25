# LEVEL-1B MODULE

from l1b.src.initL1b import initL1b
from common.io.writeToa import writeToa, readToa
from common.src.auxFunc import getIndexBand
from common.io.readFactor import readFactor, EQ_MULT, EQ_ADD, NC_EXT
import os


class l1b(initL1b):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def processModule(self):

        self.logger.info("Start of the L1B Processing Module")

        for band in self.globalConfig.bands:

            self.logger.info("Start of BAND " + band)

            toa = readToa(
                self.indir,
                self.globalConfig.ism_toa + band + '.nc'
            )

            if self.l1bConfig.do_equalization:

                self.logger.info(
                    "EODP-ALG-L1B-1010: Radiometric Correction (equalization)"
                )

                eq_mult = readFactor(
                    os.path.join(
                        self.auxdir,
                        self.l1bConfig.eq_mult + band + NC_EXT
                    ),
                    EQ_MULT
                )

                eq_add = readFactor(
                    os.path.join(
                        self.auxdir,
                        self.l1bConfig.eq_add + band + NC_EXT
                    ),
                    EQ_ADD
                )

                toa = self.equalization(
                    toa,
                    eq_add,
                    eq_mult
                )

                writeToa(
                    self.outdir,
                    self.globalConfig.l1b_toa_eq + band,
                    toa
                )

            self.logger.info(
                "EODP-ALG-L1B-1020: Absolute radiometric gain application (restoration)"
            )

            gain = self.l1bConfig.gain[
                getIndexBand(band)
            ]

            toa = self.restoration(
                toa,
                gain
            )

            writeToa(
                self.outdir,
                self.globalConfig.l1b_toa + band,
                toa
            )

            self.logger.info(
                "End of BAND " + band
            )

        self.logger.info(
            "End of the L1B Module!"
        )

    def equalization(self, toa, eq_add, eq_mult):

        toa = (toa - eq_add) / eq_mult

        return toa

    def restoration(self, toa, gain):

        toa = toa * gain

        self.logger.debug(
            'Sanity check. TOA in radiances after gain application '
            + str(toa[1, -1])
            + ' [mW/m2/sr]'
        )

        return toa