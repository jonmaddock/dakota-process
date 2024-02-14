"""Pre-process, execute and post-process a PROCESS run."""

import sys
import subprocess
import numpy as np
from typing import Dict, Any
from process.io.mfile import MFile
import regex as re
from pathlib import Path


class MfileDecoder:
    """Interprets Process's mfiles to extract responses for Dakota."""

    def __init__(self, mfile_path: Path) -> None:
        """Initialise the decoder with a path to an output mfile.

        Parameters
        ----------
        mfile_path : Path
            MFILE.DAT to extract data from
        """
        self.mfile_path = mfile_path

    def _get_data(self) -> Dict:
        """Parse mfile and return dictionary of all output data.

        Returns
        -------
        Dict
            All output data contained in mfile
        """
        mfile = MFile(Path(self.mfile_path))
        mfile_dict = {}
        for param_name in mfile.data:
            param_value = mfile.data[param_name].get_scan(-1)
            mfile_dict[param_name] = param_value

        return mfile_dict

    def _process_data(self, raw_data: Dict[str, Any]) -> Dict[str, float]:
        """Perform any required processing of raw mfile data dict.

        May include filtering for desired responses.

        Parameters
        ----------
        raw_data : Dict[str, Any]
            Entire raw output dictionary

        Returns
        -------
        Dict[str, float]
            Processed output dictionary
        """
        # Add objective function to responses dict
        responses = {"norm_objf": raw_data["norm_objf"]}

        # Extract constraints from raw_data dict
        # Find all equality and inequality constraint keys
        eq_re = re.compile(r"eq_con\d{3}")
        ineq_re = re.compile(r"ineq_con\d{3}")
        eq_constrs_keys = [key for key in raw_data.keys() if eq_re.match(key)]
        ineq_constrs_keys = [key for key in raw_data.keys() if ineq_re.match(key)]

        # Get values of constraints
        eq_constrs_dict = {
            eq_constrs_key: raw_data[eq_constrs_key]
            for eq_constrs_key in eq_constrs_keys
        }
        ineq_constrs_dict = {
            ineq_constrs_key: raw_data[ineq_constrs_key]
            for ineq_constrs_key in ineq_constrs_keys
        }

        # Only want violated constraint values
        # Coerce feasible inequality constraints (> 0) = 0.0
        # TODO Not sure if we want to mask non-violated constraint
        # values at this stage: infeasibile responses only
        vio_ineq_constrs_dict = {}
        for key, value in ineq_constrs_dict.items():
            if value > 0:
                vio_ineq_constrs_dict[key] = 0.0
            else:
                vio_ineq_constrs_dict[key] = value

        # Merge individual eq and ineq violated constraint values
        # TODO Withold individual constraint info for now to simplify Dakota responses:
        # Dakota errors if extraneous data in responses.out
        # Just include norm_objf and rms_vio_constr_res
        # responses = responses | eq_constrs_dict | vio_ineq_constrs_dict

        # Calculate RMS constraint residuals for violated constraints only
        # Create arrays from constraints dicts
        eq_constrs = np.array(list(eq_constrs_dict.values()))
        vio_ineq_constrs = np.array(list(vio_ineq_constrs_dict.values()))
        vio_constrs = np.concatenate((eq_constrs, vio_ineq_constrs))
        rms_vio_constr_res = np.sqrt(np.mean(vio_constrs**2))
        responses["rms_vio_constr_res"] = rms_vio_constr_res

        return responses

    def get_responses(self) -> Dict[str, float]:
        """Parse mfile, process it and return dict to Dakota.

        Returns
        -------
        Dict[str, float]
            Response data for Dakota

        Raises
        ------
        RuntimeError
            Raised if field is absent from processed output data
        """

        raw_data = self._get_data()
        # Perform any required processing of raw data
        processed_data = self._process_data(raw_data)

        return processed_data


# The first and second command line arguments to the script are the
# names of the Dakota parameters and results files
params_filename = sys.argv[1]
results_filename = sys.argv[2]

# Pre-processing
# Substitute parameters from Dakota's parameters file (params_filename) into the
# template, writing the IN.DAT file
# pyprepro pre-processing tool lives in /opt/Dakota/bin, on PATH
# Wants to be called via command line (requires own args)
input_template = "large_tokamak_IN.template"
input_file = "IN.DAT"  # result of processing template
subprocess.run(
    [
        "pyprepro",
        f"{input_template}",
        f"{input_file}",
        "--dakota-include",
        params_filename,
    ]
)

# Execution
# Run Process
subprocess.run(["process", "-i", "IN.DAT"])

# Post-processing
# Extract responses from MFILE
mfile_decoder = MfileDecoder("MFILE.DAT")
responses = mfile_decoder.get_responses()

# Write Dakota response file
# Dakota interprets "var" as a function value, "[var]" as a gradient
with open(results_filename, "w+") as dakota_responses_file:
    for key, value in responses.items():
        dakota_responses_file.write(f"{value}\t{key}\n")
