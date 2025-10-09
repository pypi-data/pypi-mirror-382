#!python3
"""Iterative template matching parameter tuning.

Copyright (c) 2024 European Molecular Biology Laboratory

Author: Valentin Maurer <valentin.maurer@embl-hamburg.de>
"""
import argparse
import subprocess
from sys import exit
from os import unlink
from time import time
from typing import Tuple, List, Dict

import numpy as np
from sklearn.metrics import roc_auc_score

from tme import Orientations, Density
from tme.backends import backend as be
from tme.matching_utils import generate_tempfile_name, create_mask
from tme.matching_exhaustive import MATCHING_EXHAUSTIVE_REGISTER


def parse_range(x: str):
    start, stop, step = x.split(":")
    return range(int(start), int(stop), int(step))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Refine template matching candidates using deep matching.",
    )
    io_group = parser.add_argument_group("Input / Output")
    io_group.add_argument(
        "--target",
        required=True,
        type=str,
        help="Image stack created using extract_candidates.py.",
    )
    io_group.add_argument(
        "--orientations",
        required=True,
        type=str,
        help="Path to an orientations file in a supported format. See "
        "https://kosinskilab.github.io/pyTME/reference/api/tme.orientations.Orientations.from_file.html"
        " for available options.",
    )
    io_group.add_argument(
        "--output-prefix", required=True, type=str, help="Path to write output to."
    )
    io_group.add_argument(
        "--save-pickles",
        action="store_true",
        default=False,
        help="Save intermediate results as pickle files in output directory.",
    )
    io_group.add_argument(
        "--save-orientations",
        action="store_true",
        default=False,
        help="Save orientation results in output directory.",
    )
    matching_group = parser.add_argument_group("Template Matching")
    matching_group.add_argument(
        "-i",
        "--template",
        type=str,
        required=True,
        help="Path to a template in PDB/MMCIF or other supported formats (see target).",
    )
    matching_group.add_argument(
        "--template-mask",
        type=str,
        required=False,
        help="Path to a mask for the template in a supported format (see target).",
    )
    matching_group.add_argument(
        "--ctf-file",
        type=str,
        required=False,
        default=None,
        help="Path to a file with CTF parameters. This can be a Warp/M XML file "
        "a GCTF/Relion STAR file, an MDOC file, or the output of CTFFIND4. If the file "
        " does not specify tilt angles, --tilt-angles are used.",
    )
    matching_group.add_argument(
        "--invert-target-contrast",
        action="store_true",
        default=False,
        help="Invert the target's contrast for cases where templates to-be-matched have "
        "negative values, e.g. tomograms.",
    )
    matching_group.add_argument(
        "--angular-sampling",
        required=True,
        default=None,
        help="Angular sampling rate using optimized rotational sets."
        "A lower number yields more rotations. Values >= 180 sample only the identity.",
    )
    matching_group.add_argument(
        "-s",
        "--score",
        type=str,
        default="batchFLCSphericalMask",
        choices=list(MATCHING_EXHAUSTIVE_REGISTER.keys()),
        help="Template matching scoring function.",
    )

    computation_group = parser.add_argument_group("Computation")
    computation_group.add_argument(
        "-n",
        dest="cores",
        required=False,
        type=int,
        default=4,
        help="Number of cores used for template matching.",
    )
    computation_group.add_argument(
        "--backend",
        default=be._backend_name,
        choices=be.available_backends(),
        help="Set computation backend.",
    )

    optimization_group = parser.add_argument_group("Optimization")
    optimization_group.add_argument(
        "--lowpass-range",
        type=str,
        default="0:50:5",
        help="Optimize template matching lowpass filter cutoff.",
    )
    optimization_group.add_argument(
        "--highpass-range",
        type=str,
        default="0:50:5",
        help="Optimize template matching highpass filter cutoff.",
    )
    optimization_group.add_argument(
        "--translation-uncertainty",
        type=int,
        default=8,
        help="Translational uncertainty for masking, defaults to 8.",
    )

    args = parser.parse_args()

    args.target_mask = None
    if args.lowpass_range != "None":
        args.lowpass_range = parse_range(args.lowpass_range)
    else:
        args.lowpass_range = (None,)
    if args.highpass_range != "None":
        args.highpass_range = parse_range(args.highpass_range)
    else:
        args.highpass_range = (None,)
    return args


def argdict_to_command(input_args: Dict, executable: str) -> List:
    ret = []
    for key, value in input_args.items():
        if value is None:
            continue
        elif isinstance(value, bool):
            if value:
                ret.append(key)
        else:
            ret.extend([key, value])

    ret = [str(x) for x in ret]
    ret.insert(0, executable)
    return " ".join(ret)


def run_command(command):
    ret = subprocess.run(command, capture_output=True, shell=True)
    if ret.returncode != 0:
        print(f"Error when executing: {command}.")
        print(f"Stdout: {ret.stdout.decode('utf-8')}")
        print(f"Stderr: {ret.stderr.decode('utf-8')}")
        exit(-1)

    return None


def create_matching_argdict(args) -> Dict:
    arg_dict = {
        "--target": args.target,
        "--template": args.template,
        "--template-mask": args.template_mask,
        "--output": args.match_template_path,
        "-a": args.angular_sampling,
        "-s": args.score,
        "-n": args.cores,
        "--ctf-file": args.ctf_file,
        "--invert-target-contrast": args.invert_target_contrast,
        "--backend" : args.backend,
    }
    return arg_dict


def create_postprocessing_argdict(args) -> Dict:
    arg_dict = {
        "--input-file": args.match_template_path,
        "--target-mask": args.target_mask,
        "--output-prefix": args.new_orientations_path,
        "--peak-caller": "PeakCallerMaximumFilter",
        "--num-peaks": 1,
        "--output-format": "orientations",
        "--mask-edges": True,
    }
    if args.target_mask is not None:
        arg_dict["--mask-edges"] = False
    return arg_dict


def update_orientations(
    old: Orientations, new: Orientations, args, **kwargs
) -> Orientations:
    stack_shape = Density.from_file(args.target, use_memmap=True).shape
    stack_center = np.add(np.divide(stack_shape, 2).astype(int), np.mod(stack_shape, 2))

    peak_number = new.translations[:, 0].astype(int)
    new_translations = np.add(
        old.translations[peak_number],
        np.subtract(new.translations, stack_center)[:, 1:],
    )
    ret = old.copy()
    ret.scores[:] = 0

    ret.scores[peak_number] = new.scores
    ret.translations[peak_number] = new_translations

    # The effect of --align_orientations should be handled here
    ret.rotations[peak_number] = new.rotations
    return ret


class DeepMatcher:
    def __init__(self, args, margin: float = 0.5):
        self.args = args
        self.margin = margin
        self.orientations = Orientations.from_file(args.orientations)

        match_template_args = create_matching_argdict(args)
        match_template_args["--target"] = args.target
        self.match_template_args = match_template_args

        self.filter_parameters = {}
        if args.lowpass_range:
            self.filter_parameters["--lowpass"] = 0
        if args.highpass_range:
            self.filter_parameters["--highpass"] = 0

        self.postprocess_args = create_postprocessing_argdict(args)
        self.log_file = f"{args.output_prefix}_optimization_log.txt"

        header = [
            "mean_score_positive",
            "mean_score_negative",
            "lowpass",
            "highpass",
            "auc_score",
            "duration",
        ]
        with open(self.log_file, mode="w", encoding="utf-8") as f:
            _ = f.write(",".join(header) + "\n")

    def get_initial_values(self) -> Tuple[float]:
        ret = tuple(float(x) for x in self.filter_parameters.values())
        return ret

    def format_parameters(self, parameter_values: Tuple[float]) -> Dict:
        ret = {}
        for value, key in zip(parameter_values, self.filter_parameters.keys()):
            ret[key] = value
            if isinstance(self.filter_parameters[key], bool):
                ret[key] = value > 0.5
        return ret

    def forward(self, x: Tuple[float]):
        # Label 1 -> True positive, label 0 -> false positive
        orientations_new = self(x)
        label, score = orientations_new.details, orientations_new.scores
        loss = np.add(
            (1 - label) * np.square(score),
            label * np.square(np.fmax(self.margin - score, 0.0)),
        )
        loss = loss.mean()
        return loss

    def __call__(self, x: Tuple[float]):
        start = time()
        filter_parameters = self.format_parameters(x)
        self.match_template_args.update(filter_parameters)

        if self.args.save_pickles or self.args.save_orientations:
            prefix = "_".join([str(y) for y in x])

        if self.args.save_pickles:
            pickle_path = f"{self.args.output_prefix}_{prefix}.pickle"
            self.match_template_args["--output"] = pickle_path
            self.postprocess_args["--input-file"] = pickle_path

        if self.args.save_orientations:
            orientation_path = f"{self.args.output_prefix}_{prefix}"

        match_template = argdict_to_command(
            self.match_template_args,
            executable="match_template",
        )
        run_command(match_template)

        # Assume we get a new peak for each input in the same order
        postprocess = argdict_to_command(
            self.postprocess_args,
            executable="postprocess",
        )
        run_command(postprocess)

        orientations_new = Orientations.from_file(
            f"{self.postprocess_args['--output-prefix']}.tsv"
        )
        orientations_new = update_orientations(
            new=orientations_new, old=self.orientations, args=self.args
        )

        if self.args.save_orientations:
            orientations_new.to_file(f"{orientation_path}.tsv")

        label, score = orientations_new.details, orientations_new.scores
        loss = roc_auc_score(label, score)

        mean_true = np.mean(score[label == 1])
        mean_false = np.mean(score[label == 0])
        params = ",".join([str(y) for y in x])

        with open(self.log_file, mode="a", encoding="utf-8") as f:
            _ = f.write(f"{mean_true},{mean_false},{params},{loss},{time()-start}\n")
        return orientations_new


def main():
    args = parse_args()

    args.new_orientations_path = generate_tempfile_name()
    args.match_template_path = generate_tempfile_name()

    args.box_size = np.max(Density.from_file(args.template, use_memmap=True).shape)

    args.target_mask = None
    if args.translation_uncertainty is not None:
        args.target_mask = generate_tempfile_name(suffix=".h5")
        dens = Density.from_file(args.target)
        stack_center = np.add(
            np.divide(dens.data.shape, 2).astype(int), np.mod(dens.data.shape, 2)
        ).astype(int)[1:]

        out = dens.empty
        out.data[..., :] = create_mask(
            mask_type="ellipse",
            center=stack_center,
            radius=args.translation_uncertainty,
            shape=dens.data.shape[1:],
        )
        out.to_file(args.target_mask)

    # Perhaps we need a different optimizer here to use sensible steps for each parameter
    parameters, min_loss = (), None
    match_deep = DeepMatcher(args)
    for lowpass in args.lowpass_range:
        for highpass in args.highpass_range:
            if lowpass is not None and highpass is not None:
                if lowpass >= highpass:
                    continue
            parameters = (lowpass, highpass)
            loss = match_deep.forward(parameters)
            if min_loss is None:
                min_loss, best_params = loss, parameters

            if loss < min_loss:
                min_loss, best_params = loss, parameters

    unlink(args.target_mask)
    unlink(args.new_orientations_path)

    if not args.save_pickles:
        unlink(args.match_template_path)
    print("Final output", min_loss, best_params)


if __name__ == "__main__":
    main()
