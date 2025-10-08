import numpy as np
from numpy.typing import NDArray

import emcee
from emcee.backends import HDFBackend
from multiprocessing import Pool

from .set_posterior import posterior


class MyEmceeES:
    """Class to run MCMC with emcee.

    This class is particularly design to use multivariate fuctions as posterior,
    but it can be genewralized to work with any function.
    It can managed one or more gaussian components
    and their parameters can be either linked of freezed.

    Args:
        data: `NDArray`
            Data to fit.
        posterior: `callable`
            Posterior function to use in the mcmc to compute the loglike.
        nwalkers: `int`
            Number of walkers initialized in the MCMC.
        nsteps: `int`
            Number of steps to run.
        ncomp: `int`
            Number of model components to use.
        par_per_comp: `int`
            Number of parameters per component.
        qmin: `NDArray`
            Lower limits for priors.
        qmax: `NDArray`
            Upper limits for priors.
        p0: `NDArray`  or `None`, optional
            Initial guess for the parameters.
            If `None`, uniform distribution between qmin and qmax will be used. Defult is `None`.
        fix_params: `NDArray` or `None`, optional
            Array containing the fixed parameters. If None, no parameters will be fixed. Defaul is `None`
        lnk_params: `NDArray` or `None`, optional
            Array containing the linked parameters. If None, no parameters will be linked together.
            Defaul is `None`
        save_chains: `bool`, optional
            If True, the chains will be saved in an HDF5 file. Default is False.
        hdf_filename: `str`, optional
            Name of the HDF5 file to save the chains. Default is "mcmc_chains.h5".
        parallel: `bool`, optional
            If True, use multiprocessing to run the MCMC on multiple processor.
            If False, run the MCMC in a single process. Default is False.
        from_previous_run: `bool`, optional
            If True, load a previous MCMC run from an HDF5 file. Default is False.
        hdf_backend_kwargs: `dict` or `None`, optional
            Dictionary containing the parameters to use for the HDFBackend.
    """

    def __init__(
        self,
        data: NDArray | None = None,
        nwalkers: int | None = None,
        nsteps: int | None = None,
        ncomp: int | None = None,
        par_per_comp: int | None = None,
        qmin: NDArray | None = None,
        qmax: NDArray | None = None,
        pmodel: str | None = None,
        p0: NDArray | None = None,
        fix_params: NDArray | None = None,
        lnk_params: NDArray | None = None,
        save_chains: bool = False,
        hdf_filename: str = "mcmc_chains.h5",
        parallel: bool = False,  # TODO: now with parallel is slower!
        from_previous_run: bool = False,
        hdf_backend_kwargs: dict | None = None,
    ):
        self.from_previous_run = from_previous_run
        if not self.from_previous_run:
            self.data = data
            self.pmodel = pmodel
            self.nwalkers = nwalkers
            self.nsteps = nsteps
            self.ncomp = ncomp
            self.par_per_comp = par_per_comp
            self.ndim = (
                (ncomp * par_per_comp) + ncomp - 1
                if self.ncomp > 1
                else (ncomp * par_per_comp) + ncomp
            )
            self.qmin = qmin
            self.qmax = qmax
            self.fix_params = fix_params
            self.lnk_params = lnk_params
            self.chain = None

            self.p0 = (
                np.array(
                    [
                        np.random.uniform(self.qmin, self.qmax)
                        for _ in range(self.nwalkers)
                    ]
                )
                if p0 is None
                else p0
            )

            self.p0[:, -2] = np.random.uniform(0.3, 0.6, size=self.nwalkers)
            self.p0[:, -1] = np.random.uniform(0.0, 0.3, size=self.nwalkers)

            self.bpars = None

            self.pool = None
            if parallel:
                self.pool = Pool()

            backend = None
            if save_chains:
                backend = emcee.backends.HDFBackend(hdf_filename)
                backend.reset(nwalkers=self.nwalkers, ndim=self.ndim)

            # set the sampler
            self.sampler = emcee.EnsembleSampler(
                nwalkers=self.nwalkers,
                ndim=self.ndim,
                log_prob_fn=posterior,
                kwargs={
                    "data": self.data,
                    "qmin": self.qmin,
                    "qmax": self.qmax,
                    "component": self.ncomp,
                    "stride": self.par_per_comp,
                    "fix_params": self.fix_params,
                    "lnk_params": self.lnk_params,
                    "pmodel": self.pmodel,
                },
                moves=[
                    (emcee.moves.DEMove(), 0.8),
                    (emcee.moves.DESnookerMove(), 0.2),
                ],
                backend=backend,
                pool=self.pool,
            )
        else:
            self.sampler = self.load_mcmc_run(**hdf_backend_kwargs)

    def run_emcee(self):
        """Run the MCMC using emcee.

        Args:
            parallel: `bool`, optional
                If True, use multiprocessing to run the MCMC on multiple processor.
                If False, run the MCMC in a single process. Default is False.
        """
        self.sampler.run_mcmc(self.p0, self.nsteps, progress=True)

    def get_chain(self, **kwargs) -> NDArray:
        """Get the chain of samples.

        Args:
            kwargs:
                Parameters of get_chain emcee's method (*thin*, *flat*, *discard*).

        Returns:
            chain: `NDArray`
                Chain of samples.
        """
        return self.sampler.get_chain(**kwargs)

    @staticmethod
    def get_model_parameters(
        sampler: emcee.EnsembleSampler | emcee.backends.HDFBackend,
        which: str,
        percentile: list[float] = [16.0, 50.0, 84.0],
        **kwargs
    ) -> NDArray:
        """Obtain the model parameters from the chain.

        Args:
            sampler: `EnsembleSampler` or `HDFBackend`
                Emcee sampler object containing the MCMC run.
            which: `str`
                How to retrieve the model parameter.
                - *percentiles*: the parameters will be returned at the specified percentiles.
                - *maxln*: the parameters that represent the maximum loglikelihood.
            percentile: `list` of `float`, optional
                Percentiles to use, default are [16., 50., 84.].
            kwargs:
                Parameters of get_chain and get_log_prob emcee methods (*thin*, *flat*, *discard*).

        Returns:
            pars: `NDArray`
                Parameters set from the chain.
        """
        if which == "maxln":
            maxln = sampler.get_log_prob(**kwargs).argmax()
            return sampler.get_chain(**kwargs)[maxln]
        else:
            return np.percentile(sampler.get_chain(**kwargs), percentile, axis=0)

    @staticmethod
    def load_mcmc_run(**kwargs) -> HDFBackend:
        """Load a previous MCMC run saved in an HDF5 file.

        Args:
            kwargs:
                Parameters of the HDFBackend emcee's method.

        Returns:
            backend: `HDFBackend`
                HDFBackend object containing the MCMC run.
        """
        return emcee.backends.HDFBackend(**kwargs)
