from architector import build_complex, convert_io_molecule
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging
from pathlib import Path
from tqdm import tqdm

from .dataset import SampleDataset, Sample
from .io import save_xyz, save_chrg, save_uhf


class Optimiser:
    def __init__(
        self,
        root: Path,
        settings: dict[str],
        nprocs: int | None = 1,
        logger: logging.Logger | None = None,
    ):
        """
        The Optimiser class can create .xyz geometries from a given `SampleDataset` using Architector's build_complex() method.

        Args:
            root (Path): Root folder where generated output structures are stored.
            settings (dict[str]): Settings for Arcitector.build_complex(). See details at https://github.com/lanl/Architector.
            nprocs (int | None, optional): Number of processes for calculations. Recommended to set equal to the number of CPUs.
                                        Choosing `None` sets nprocs to max available number of processor.
            logger (logging.Logger | None, optional): Logger used for logging. If None, a default logger will be created.

        Raises:
            ValueError: If nprocs is less than 1.
        """
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.settings = settings
        self.nprocs = nprocs
        self.logger = self.default_logger() if logger is None else logger

        if self.nprocs < 1 and not self.nprocs == None:
            raise ValueError(
                "For the number of processes, please use an integer larger than 1."
            )

    def run(self, dataset: SampleDataset) -> None:
        """
        Run the optimization process on the provided dataset.

        Args:
            dataset (SampleDataset): The dataset on which the optimization will be performed.
        """
        self.logger.info(f"Start optimisation")
        if self.nprocs == 1:
            self.batch_opt(dataset)
        else:
            self.parallel_opt(dataset)

    def batch_opt(self, dataset: SampleDataset) -> None:
        """
        Perform batch optimization on the provided dataset.

        Args:
            dataset (SampleDataset): The dataset containing samples to be optimized.
        """
        self.logger.info(f"Batch optimisation on {len(dataset)} samples.")
        for sample in tqdm(dataset, desc="Processing", unit="sample"):
            self.optimise(sample, self.settings)
        self.logger.info(f"Finished batch optimisation.")

    def parallel_opt(self, dataset: "SampleDataset") -> None:
        """
        Perform parallel optimization on the provided dataset.

        Args:
            dataset (SampleDataset): The dataset containing samples to be optimized.
        """
        self.logger.info(
            f"Parallel optimisation on {len(dataset)} samples. Number of processes: {self.nprocs}"
        )
        # threading
        # with ThreadPoolExecutor() as executor:
        #     executor.map(self.optimise, [(sample, self.settings) for sample in dataset])

        # multiprocesses
        with ProcessPoolExecutor(max_workers=self.nprocs) as executor:
            settings = [self.settings] * self.nprocs
            executor.map(self.optimise, dataset.samples, settings)
        self.logger.info(f"Finished parallel optimisation.")

    def optimise(self, sample: Sample, settings: dict) -> None:
        """
        Optimise a single `Sample` and create an output directory named `sample.uid` in the root folder.

        Args:
            sample (Sample): The sample to be optimized.
            settings (dict): Optimization settings.
        """
        self.logger.debug(f"Optimise sample {sample.uid}")

        fp = self.root / sample.uid
        fp.mkdir(parents=True, exist_ok=True)

        try:
            # Construct input for architector.build_complex()
            inp = self.get_architector_input(sample, settings)

            self.logger.debug(f"Run architector.build_complex()")
            out = build_complex(inp)

            if not isinstance(out, dict):
                raise ValueError("Architector output is not a dict.")

            if len(out) == 0:
                raise ValueError("Empty dictionary was produced.")

            # Write the optimised geometry to disk
            self.write_output(out, fp)

        except Exception as e:
            error_message = f"Error processing data: {e}"
            self.logger.debug(error_message)

            # Create local loggers to write .err files
            logerr = self.get_logger("LocErr", fp / ".err")
            logerr.debug(error_message)
            self.delete_logger(logerr)
            return

        self.logger.debug("Success.")

    def get_architector_input(self, sample: Sample, settings: dict[str]) -> dict[str]:
        """
        Construct the input dictionary for the Architector build_complex() method.

        Args:
            sample (Sample): The sample object from which input data will be extracted.
            settings (dict[str]): Additional settings for the Architector build.

        Returns:
            dict[str]: The input dictionary containing sample data and specified settings.
        """
        return {**sample.to_dict(), "parameters": {k: v for k, v in settings.items()}}

    def write_output(self, output: dict, save_dir: Path, name: str = "sample") -> None:
        """Save the output of Architector's build_complex() function in a separate directory.

        Args:
            output (dict): Output dictionary returned by Architector's build_complex() function.
            save_dir (Path): Path to the output directory, where all files will be saved.
            name (str, optional): Name of the files. Defaults to "sample".
        """
        out = output[list(output.keys())[0]]

        mol = convert_io_molecule(out["mol2string"])
        charge = out["total_charge"]
        n_unpels = out["calc_n_unpaired_electrons"]

        mol_path = str(save_dir / f"{name}.xyz")
        charge_path = str(save_dir / ".CHRG")
        uhf_path = str(save_dir / ".UHF")

        save_xyz(mol, mol_path)
        save_chrg(charge, charge_path)
        save_uhf(n_unpels, uhf_path)
        self.logger.debug(f"Saved to {save_dir}")

    def default_logger(self) -> logging.Logger:
        """
        Creates and configures a default logger.

        Returns:
            logging.Logger: A logger object that can be used for logging optimisation processes.
        """
        return self.get_logger(
            f"{self.__class__.__name__}Logger", self.root / "optimisation.log"
        )

    def get_logger(self, name: str, log_file_path: Path) -> logging.Logger:
        """
        Create and configure a logger with the given name and log file path.

        Args:
            name (str): Name for the logger.
            log_file_path (Path): Path to the log file.

        Returns:
            logging.Logger: A configured logger instance.
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)

        return logger

    def delete_logger(self, logger: logging.Logger):
        """
        Remove all handlers from the provided logger.

        Args:
            logger (logging.Logger): The logger instance from which handlers will be removed.
        """
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)
