# LEVEL-1B MODULE

from l1b.src.initL1b import initL1b
from common.io.writeToa import writeToa, readToa
from common.src.auxFunc import getIndexBand
from common.io.readFactor import readFactor, EQ_MULT, EQ_ADD, NC_EXT
import numpy as np
import os
import matplotlib.pyplot as plt


class l1b(initL1b):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

    def processModule(self):

        self.logger.info("Start of the L1B Processing Module")

        for band in self.globalConfig.bands:

            self.logger.info("Start of BAND " + band)

            # Read TOA - output of the ISM in Digital Numbers
            # -------------------------------------------------------------------------------
            toa = readToa(
                self.indir,
                self.globalConfig.ism_toa + band + '.nc'
            )

            # Keep original DN input for comparison plots
            toa_original = toa.copy()

            # Equalization (radiometric correction)
            # -------------------------------------------------------------------------------
            if self.l1bConfig.do_equalization:

                self.logger.info(
                    "EODP-ALG-L1B-1010: Radiometric Correction (equalization)"
                )

                # Read multiplicative and additive equalization factors
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

                # Equalization
                toa = self.equalization(
                    toa,
                    eq_add,
                    eq_mult
                )

                # Save equalized DN output
                writeToa(
                    self.outdir,
                    self.globalConfig.l1b_toa_eq + band,
                    toa
                )

            # Restitution (absolute radiometric gain)
            # -------------------------------------------------------------------------------
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

            # -------------------------------------------------------------------------------
            # Generate equalized and non-equalized versions for comparison plot
            # -------------------------------------------------------------------------------

            eq_mult_plot = readFactor(
                os.path.join(
                    self.auxdir,
                    self.l1bConfig.eq_mult + band + NC_EXT
                ),
                EQ_MULT
            )

            eq_add_plot = readFactor(
                os.path.join(
                    self.auxdir,
                    self.l1bConfig.eq_add + band + NC_EXT
                ),
                EQ_ADD
            )

            # Equalized + restored
            toa_eq_plot = self.equalization(
                toa_original.copy(),
                eq_add_plot,
                eq_mult_plot
            )

            toa_eq_plot = self.restoration(
                toa_eq_plot,
                gain
            )

            # Non-equalized + restored
            toa_noneq_plot = self.restoration(
                toa_original.copy(),
                gain
            )

            # Target ISRF radiance
            toa_target = readToa(
                self.indir,
                self.globalConfig.ism_toa_isrf + band + '.nc'
            )

            # Write output TOA
            # -------------------------------------------------------------------------------
            writeToa(
                self.outdir,
                self.globalConfig.l1b_toa + band,
                toa
            )

            # Original single-output plot
            self.plotL1bToa(
                toa,
                self.outdir,
                band
            )

            # Combined comparison plot
            self.plotL1bComparison(
                toa_target,
                toa_eq_plot,
                toa_noneq_plot,
                self.outdir,
                band
            )

            self.logger.info(
                "End of BAND " + band
            )

        self.logger.info(
            "End of the L1B Module!"
        )

    def equalization(self, toa, eq_add, eq_mult):
        """
        Equalization. Apply an offset and a gain.
        :param toa: TOA in DN
        :param eq_add: Offset in DN
        :param eq_mult: Gain factor, adimensional
        :return: TOA in DN, equalized
        """

        toa = (toa - eq_add) / eq_mult

        return toa

    def restoration(self, toa, gain):
        """
        Absolute Radiometric Gain - restore back to radiances
        :param toa: TOA in DN
        :param gain: gain in [rad/DN]
        :return: TOA in radiances [mW/sr/m2]
        """

        toa = toa * gain

        self.logger.debug(
            'Sanity check. TOA in radiances after gain application '
            + str(toa[1, -1])
            + ' [mW/m2/sr]'
        )

        return toa

    def plotL1bToa(
            self,
            toa_l1b,
            outputdir,
            band):

        idalt = int(
            toa_l1b.shape[0] / 2
        )

        plt.figure()

        plt.plot(
            toa_l1b[idalt, :],
            label='TOA L1B'
        )

        plt.title(
            'Equalization and restoration for ' + band
        )

        plt.xlabel(
            'ACT pixel [-]'
        )

        plt.ylabel(
            'TOA [mW/m2/sr]'
        )

        plt.grid()
        plt.legend()

        band_clean = str(
            band
        ).strip()

        filename = os.path.join(
            outputdir,
            f"l1b_toa_{band_clean}.png"
        )

        plt.savefig(
            filename
        )

        plt.close()

    def plotL1bComparison(
            self,
            toa_target,
            toa_eq,
            toa_noneq,
            outputdir,
            band):

        idalt = int(
            toa_target.shape[0] / 2
        )

        plt.figure()

        # Blue = target ISRF
        plt.plot(
            toa_target[idalt, :],
            'b-',
            label='Target ISRF'
        )

        # Black = equalized/calibrated L1B
        plt.plot(
            toa_eq[idalt, :],
            'k-',
            label='Equalized'
        )

        # Red = non-equalized L1B
        plt.plot(
            toa_noneq[idalt, :],
            'r-',
            label='Non-equalized'
        )

        plt.title(
            'L1B equalization and restoration - ' + band
        )

        plt.xlabel(
            'ACT pixel [-]'
        )

        plt.ylabel(
            'TOA [mW/m2/sr]'
        )

        plt.grid()
        plt.legend()

        band_clean = str(
            band
        ).strip()

        filename = os.path.join(
            outputdir,
            f"l1b_comparison_{band_clean}.png"
        )

        plt.savefig(
            filename
        )

        plt.close()