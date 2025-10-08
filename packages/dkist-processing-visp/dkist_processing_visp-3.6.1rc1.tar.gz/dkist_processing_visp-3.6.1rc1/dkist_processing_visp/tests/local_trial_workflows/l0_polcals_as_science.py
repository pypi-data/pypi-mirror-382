"""For running just PolCal frames as science data and saving their outputs."""

import argparse
import json
import logging
import sys
from dataclasses import asdict
from random import randint
from typing import Literal

from astropy.io import fits
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks import AssembleVispMovie
from dkist_processing_visp.tasks import MakeVispMovieFrames
from dkist_processing_visp.tasks.background_light import BackgroundLightCalibration
from dkist_processing_visp.tasks.dark import DarkCalibration
from dkist_processing_visp.tasks.geometric import GeometricCalibration
from dkist_processing_visp.tasks.instrument_polarization import InstrumentPolarizationCalibration
from dkist_processing_visp.tasks.l1_output_data import VispAssembleQualityData
from dkist_processing_visp.tasks.lamp import LampCalibration
from dkist_processing_visp.tasks.science import ScienceCalibration
from dkist_processing_visp.tasks.solar import SolarCalibration
from dkist_processing_visp.tasks.visp_base import VispTaskBase
from dkist_processing_visp.tasks.write_l1 import VispWriteL1Frame
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadBackgroundCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadCalibratedData
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadDarkCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadGeometricCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadInputParsing
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadInstPolCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadLampCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    LoadPolcalAsScience,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadSolarCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    ParseCalOnlyL0InputData,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveBackgroundCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveCalibratedData
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveDarkCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveGeometricCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveInputParsing
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveInstPolCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveLampCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    SavePolcalAsScience,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveSolarCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetAxesTypes
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    SetCadenceConstants,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetNumModstates
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetObserveExpTime
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    SetObserveIpStartTime,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetPolarimeterMode
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import ValidateL1Output
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    set_observe_wavelength_task,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import tag_inputs_task
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    translate_122_to_214l0_task,
)

__version__ = "PCAS"

QUALITY = False
try:
    import dkist_quality

    QUALITY = True
except ModuleNotFoundError:
    logging.warning("Could not find dkist-quality")


class CreateInputDatasetParameterDocument(WorkflowTaskBase):
    def run(self) -> None:
        relative_path = "input_dataset_parameters.json"
        self.write(
            data=InputDatasetPartDocumentList(
                doc_list=self.input_dataset_document_simple_parameters_part
            ),
            relative_path=relative_path,
            tags=VispTag.input_dataset_parameters(),
            encoder=basemodel_encoder,
            overwrite=True,
        )
        logger.info(f"Wrote input dataset parameter doc to {relative_path}")

    @property
    def input_dataset_document_simple_parameters_part(self):
        parameters_list = []
        value_id = randint(1000, 2000)
        for pn, pv in asdict(
            VispInputDatasetParameterValues(
                visp_background_on=False,
                visp_geo_upsample_factor=10000,
                visp_polcal_num_spatial_bins=2560,
            )
        ).items():
            values = [
                {
                    "parameterValueId": value_id,
                    "parameterValue": json.dumps(pv),
                    "parameterValueStartDate": "1946-11-20",
                }
            ]
            parameter = {"parameterName": pn, "parameterValues": values}
            parameters_list.append(parameter)

        return parameters_list


class TagPolcalAsScience(VispTaskBase):
    """Do."""

    def run(self) -> None:
        """Do."""
        # First, tag the polcal frames as observe frames with the correct stuff
        num_raster_set = set()
        for cs_step in range(self.constants.num_cs_steps):
            for modstate in range(1, self.constants.num_modstates + 1):
                file_list = list(
                    self.read(
                        tags=[
                            VispTag.task_polcal(),
                            VispTag.cs_step(cs_step),
                            VispTag.modstate(modstate),
                        ]
                    )
                )
                num_raster_set.add(len(file_list))
                for raster_step, file_name in enumerate(file_list):
                    og_tags = self.tags(file_name)
                    logging.info(
                        f"Raw frame {file_name} at {cs_step = } and {modstate = } has {og_tags = }"
                    )
                    self.scratch._tag_db.clear_value(file_name)
                    logging.info(f"\tafter removing, the tags are {self.tags(file_name)}")

                    hdul = fits.open(file_name, mode="update")
                    idx = 0
                    if hdul[idx].data is None:
                        idx = 1
                    hdul[idx].header["VSPSTP"] = raster_step
                    hdul.flush()
                    del hdul

                    new_tags = [
                        VispTag.task_observe(),
                        VispTag.map_scan(cs_step + 1),
                        VispTag.raster_step(raster_step),
                        VispTag.frame(),
                        VispTag.modstate(modstate),
                        VispTag.input(),
                        VispTag.readout_exp_time(self.constants.observe_readout_exp_times[0]),
                    ]
                    logging.info(f"\tadding {new_tags = }")
                    self.tag(file_name, new_tags)
                    final_tags = self.tags(file_name)
                    logging.info(f"\tafter retagging tags are {final_tags}")

        if len(num_raster_set) != 1:
            raise ValueError(
                "Expected to find the same number of files for each (CS step, modstate), but did not. "
                f"Set of counts is {num_raster_set}"
            )

        num_raster_steps = num_raster_set.pop()
        logging.info(f"Found {num_raster_steps} raster steps")
        # Now update the num[map, raster] constants. We'll call each CS step a "map"
        self.constants._update(
            {
                VispBudName.num_raster_steps.value: num_raster_steps,
                VispBudName.num_map_scans.value: self.constants.num_cs_steps,
            }
        )


def write_L1_files_task(prefix: str = ""):
    """Do."""
    if len(prefix) > 0 and prefix[-1] != "_":
        prefix += "_"

    class WritePolcalL1Files(VispWriteL1Frame):
        """Do."""

        def l1_filename(self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]):
            """Do."""
            wavelength = str(round(header["LINEWAV"] * 1000)).zfill(8)
            cs_step = header["VSPMAP"]
            raster_step = header["VSPSTP"]
            return f"{prefix}CS_STEP_{cs_step:02n}_{raster_step:02n}_{wavelength}_{stokes}_L1.fits"

    return WritePolcalL1Files


def main(
    scratch_path: str,
    suffix: str = "fits",
    prefix: str = "",
    recipe_run_id: int = 2,
    skip_translation: bool = False,
    only_translate: bool = False,
    load_parse: bool = False,
    load_dark: bool = False,
    load_background: bool = False,
    load_lamp: bool = False,
    load_geometric: bool = False,
    load_solar: bool = False,
    load_inst_pol: bool = False,
    load_polcal_as_science: bool = False,
    load_calibrated_data: bool = False,
    dummy_wavelength: float = 630.0,
):
    """Run the damn thing."""
    with ManualProcessing(
        workflow_path=scratch_path,
        recipe_run_id=recipe_run_id,
        testing=True,
        workflow_name="visp-l0-pipeline",
        workflow_version="GROGU",
    ) as manual_processing_run:
        if not skip_translation:
            manual_processing_run.run_task(task=translate_122_to_214l0_task(suffix))
        if only_translate:
            return
        manual_processing_run.run_task(task=CreateInputDatasetParameterDocument)
        if load_parse:
            manual_processing_run.run_task(task=LoadInputParsing)
        else:
            manual_processing_run.run_task(task=tag_inputs_task(suffix))
            manual_processing_run.run_task(task=ParseCalOnlyL0InputData)
            manual_processing_run.run_task(
                task=set_observe_wavelength_task(wavelength=dummy_wavelength)
            )
            manual_processing_run.run_task(task=SetObserveIpStartTime)
            manual_processing_run.run_task(task=SetObserveExpTime)
            manual_processing_run.run_task(task=SetPolarimeterMode)
            manual_processing_run.run_task(task=SetNumModstates)
            manual_processing_run.run_task(task=SetCadenceConstants)
            manual_processing_run.run_task(task=SetAxesTypes)
            manual_processing_run.run_task(task=SaveInputParsing)

        if load_dark:
            manual_processing_run.run_task(task=LoadDarkCal)
        else:
            manual_processing_run.run_task(task=DarkCalibration)
            manual_processing_run.run_task(task=SaveDarkCal)

        if load_background:
            manual_processing_run.run_task(task=LoadBackgroundCal)
        else:
            manual_processing_run.run_task(task=BackgroundLightCalibration)
            manual_processing_run.run_task(task=SaveBackgroundCal)

        if load_lamp:
            manual_processing_run.run_task(task=LoadLampCal)
        else:
            manual_processing_run.run_task(task=LampCalibration)
            manual_processing_run.run_task(task=SaveLampCal)

        if load_geometric:
            manual_processing_run.run_task(task=LoadGeometricCal)
        else:
            manual_processing_run.run_task(task=GeometricCalibration)
            manual_processing_run.run_task(task=SaveGeometricCal)

        if load_solar:
            manual_processing_run.run_task(task=LoadSolarCal)
        else:
            manual_processing_run.run_task(task=SolarCalibration)
            manual_processing_run.run_task(task=SaveSolarCal)

        if load_inst_pol:
            manual_processing_run.run_task(task=LoadInstPolCal)
        else:
            manual_processing_run.run_task(task=InstrumentPolarizationCalibration)
            manual_processing_run.run_task(task=SaveInstPolCal)

        if load_polcal_as_science:
            manual_processing_run.run_task(task=LoadPolcalAsScience)
        else:
            manual_processing_run.run_task(task=TagPolcalAsScience)
            manual_processing_run.run_task(task=SavePolcalAsScience)

        if load_calibrated_data:
            manual_processing_run.run_task(task=LoadCalibratedData)
        else:
            manual_processing_run.run_task(task=ScienceCalibration)
            manual_processing_run.run_task(task=SaveCalibratedData)

        manual_processing_run.run_task(task=write_L1_files_task(prefix=prefix))
        manual_processing_run.run_task(task=QualityL1Metrics)
        manual_processing_run.run_task(task=VispAssembleQualityData)
        manual_processing_run.run_task(task=ValidateL1Output)
        manual_processing_run.run_task(task=MakeVispMovieFrames)
        manual_processing_run.run_task(task=AssembleVispMovie)

        # Test some downstream services
        if QUALITY:
            manual_processing_run.run_task(task=CreateTrialQualityReport)
        else:
            logger.warning("Did NOT make quality report pdf because dkist-quality is not installed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate PolCals with the ViSP DC Science pipeline"
    )
    parser.add_argument("scratch_path", help="Location to use as the DC 'scratch' disk")
    parser.add_argument(
        "-i",
        "--run-id",
        help="Which subdir to use. This will become the recipe run id",
        type=int,
    )
    parser.add_argument("--prefix", help="File prefix to add to L1 output frames", default="")
    parser.add_argument("--suffix", help="File suffix to treat as INPUT frames", default="fits")
    parser.add_argument(
        "-w",
        "--wavelength",
        help="Dummy wavelength to use for loading parameters, etc.",
        type=float,
        default=630.0,
    )
    parser.add_argument(
        "-T",
        "--skip-translation",
        help="Skip the translation of raw 122 l0 frames to 214 l0",
        action="store_true",
    )
    parser.add_argument(
        "-t", "--only-translate", help="Do ONLY the translation step", action="store_true"
    )
    parser.add_argument(
        "-I", "--load-input-parsing", help="Load tags on input files", action="store_true"
    )
    parser.add_argument(
        "-D",
        "--load-dark",
        help="Load dark calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-B",
        "--load-background",
        help="Load background calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-L",
        "--load-lamp",
        help="Load lamp calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-G",
        "--load-geometric",
        help="Load geometric calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-S",
        "--load-solar",
        help="Load solar calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-P",
        "--load-inst-pol",
        help="Load instrument polarization calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-O",
        "--load-polcal-as-science",
        help="Don't re-make the polcal-as-science frames",
        action="store_true",
    )
    parser.add_argument(
        "-C", "--load-calibrated-data", help="Load CALIBRATED 'science' frames", action="store_true"
    )
    args = parser.parse_args()
    logging.info(f"Called as {' '.join(sys.argv)}")
    sys.exit(
        main(
            scratch_path=args.scratch_path,
            suffix=args.suffix,
            prefix=args.prefix,
            recipe_run_id=args.run_id,
            skip_translation=args.skip_translation,
            only_translate=args.only_translate,
            load_parse=args.load_input_parsing,
            load_dark=args.load_dark,
            load_background=args.load_background,
            load_lamp=args.load_lamp,
            load_geometric=args.load_geometric,
            load_solar=args.load_solar,
            load_inst_pol=args.load_inst_pol,
            load_polcal_as_science=args.load_polcal_as_science,
            load_calibrated_data=args.load_calibrated_data,
            dummy_wavelength=args.wavelength,
        )
    )
