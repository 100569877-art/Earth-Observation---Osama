
from ism.src.initIsm import initIsm
import numpy as np
from common.io.writeToa import writeToa
from common.plot.plotMat2D import plotMat2D
from common.plot.plotF import plotF

class detectionPhase(initIsm):

    def __init__(self, auxdir, indir, outdir):
        super().__init__(auxdir, indir, outdir)

        # Initialise the random see for the PRNU and DSNU
        np.random.seed(self.ismConfig.seed)


    def compute(self, toa, band):

        self.logger.info("EODP-ALG-ISM-2000: Detection stage")

        # Irradiance to photons conversion
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-2010: Irradiances to Photons")
        area_pix = self.ismConfig.pix_size * self.ismConfig.pix_size # [m2]
        toa = self.irrad2Phot(toa, area_pix, self.ismConfig.t_int, self.ismConfig.wv[int(band[-1])])

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [ph]")

        # Photon to electrons conversion
        # -------------------------------------------------------------------------------
        self.logger.info("EODP-ALG-ISM-2030: Photons to Electrons")
        toa = self.phot2Electr(toa, self.ismConfig.QE)

        self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

        if self.ismConfig.save_after_ph2e:
            saveas_str = self.globalConfig.ism_toa_e + band
            writeToa(self.outdir, saveas_str, toa)

        # PRNU
        # -------------------------------------------------------------------------------
        if self.ismConfig.apply_prnu:

            self.logger.info("EODP-ALG-ISM-2020: PRNU")
            toa = self.prnu(toa, self.ismConfig.kprnu)

            self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

            if self.ismConfig.save_after_prnu:
                saveas_str = self.globalConfig.ism_toa_prnu + band
                writeToa(self.outdir, saveas_str, toa)

        # Dark-signal
        # -------------------------------------------------------------------------------
        if self.ismConfig.apply_dark_signal:

            self.logger.info("EODP-ALG-ISM-2020: Dark signal")
            toa = self.darkSignal(toa, self.ismConfig.kdsnu, self.ismConfig.T, self.ismConfig.Tref,
                                  self.ismConfig.ds_A_coeff, self.ismConfig.ds_B_coeff)

            self.logger.debug("TOA [0,0] " +str(toa[0,0]) + " [e-]")

            if self.ismConfig.save_after_ds:
                saveas_str = self.globalConfig.ism_toa_ds + band
                writeToa(self.outdir, saveas_str, toa)

        # Bad/dead pixels
        # -------------------------------------------------------------------------------
        if self.ismConfig.apply_bad_dead:

            self.logger.info("EODP-ALG-ISM-2050: Bad/dead pixels")
            toa = self.badDeadPixels(toa,
                               self.ismConfig.bad_pix,
                               self.ismConfig.dead_pix,
                               self.ismConfig.bad_pix_red,
                               self.ismConfig.dead_pix_red)


        # Write output TOA
        # -------------------------------------------------------------------------------
        if self.ismConfig.save_detection_stage:
            saveas_str = self.globalConfig.ism_toa_detection + band

            writeToa(self.outdir, saveas_str, toa)

            title_str = 'TOA after the detection phase [e-]'
            xlabel_str='ACT'
            ylabel_str='ALT'
            plotMat2D(toa, title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

            idalt = int(toa.shape[0]/2)
            saveas_str = saveas_str + '_alt' + str(idalt)
            plotF([], toa[idalt,:], title_str, xlabel_str, ylabel_str, self.outdir, saveas_str)

        return toa

    def irrad2Phot(self, toa, area_pix, tint, wv):

        h = 6.62606896e-34
        c = 2.99792458e8

        # Input is mW/m2 -> convert to W/m2
        toa_w = toa * 1e-3

        # Energy reaching one detector pixel
        energy_in = toa_w * area_pix * tint

        # Photon energy
        energy_photon = h * c / wv

        # Number of photons
        toa_ph = energy_in / energy_photon

        return toa_ph

    def phot2Electr(self, toa, QE):

        toae = toa * QE

        return toae

    def badDeadPixels(
            self, toa,
            bad_pix, dead_pix,
            bad_pix_red, dead_pix_red):

        toa_act = toa.shape[1]

        n_bad = int(
            toa_act * bad_pix / 100.0
        )

        n_dead = int(
            toa_act * dead_pix / 100.0
        )

        if n_bad > 0:
            step_bad = int(
                toa_act / n_bad
            )

            idx_bad = range(
                5,
                toa_act,
                step_bad
            )

            toa[:, list(idx_bad)] *= (
                    1.0 - bad_pix_red
            )

        if n_dead > 0:
            step_dead = int(
                toa_act / n_dead
            )

            idx_dead = range(
                0,
                toa_act,
                step_dead
            )

            toa[:, list(idx_dead)] *= (
                    1.0 - dead_pix_red
            )

        return toa

    def prnu(self, toa, kprnu):

        ncolumns = toa.shape[1]

        prnu_act = (
                np.random.normal(
                    0.0,
                    1.0,
                    ncolumns
                )
                * kprnu
        )

        toa = toa * (
                1.0 + prnu_act[np.newaxis, :]
        )

        return toa

    def darkSignal(
            self, toa, kdsnu,
            T, Tref,
            ds_A_coeff, ds_B_coeff):

        ncolumns = toa.shape[1]

        dsnu = (
                np.abs(
                    np.random.normal(
                        0.0,
                        1.0,
                        ncolumns
                    )
                )
                * kdsnu
        )

        Sd = (
                ds_A_coeff
                * (T / Tref) ** 3
                * np.exp(
            -ds_B_coeff
            * (1.0 / T - 1.0 / Tref)
        )
        )

        dark_signal = Sd * (1.0 + dsnu)

        toa = toa + dark_signal[np.newaxis, :]

        return toa
