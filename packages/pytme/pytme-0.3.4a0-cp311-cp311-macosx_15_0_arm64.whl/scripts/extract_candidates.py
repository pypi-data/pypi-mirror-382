#!python3
"""Prepare orientations stack for refinement.

Copyright (c) 2023 European Molecular Biology Laboratory

Author: Valentin Maurer <valentin.maurer@embl-hamburg.de>
"""
import argparse
from os import unlink
from os.path import splitext, basename

import numpy as np
from collections import defaultdict

from tme.parser import StarParser
from tme import Density, Orientations
from tme.matching_utils import generate_tempfile_name
from tme.rotations import (
    align_vectors,
    euler_from_rotationmatrix,
    euler_to_rotationmatrix,
)


class ProgressBar:
    """
    ASCII progress bar.
    """

    def __init__(self, message: str, nchars: int, total: int):
        self._size = nchars - len(message) - (len(str(total)) + 2) * 2
        self._message = message
        self._total = total

    def update(self, cur):
        x = int(cur * self._size / self._total)
        print(
            "%s[%s%s] %i/%i\r"
            % (self._message, "#" * x, "." * (self._size - x), cur, self._total),
            end="",
        )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract matching candidates for further refinement.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    io_group = parser.add_argument_group("Input / Output")
    io_group.add_argument(
        "--orientations",
        required=True,
        type=str,
        help="Star file with picks and micrograph names.",
    )
    io_group.add_argument(
        "--orientations-scaling",
        required=False,
        type=float,
        default=1.0,
        help="Factor to map candidate coordinates onto the target. Only relevant if "
        "target sampling rate differs from candidate orientation sampling rate.",
    )
    io_group.add_argument(
        "-o",
        "--output-prefix",
        required=True,
        type=str,
        help="Output prefix to use.",
    )

    alignment_group = parser.add_argument_group("Alignment")
    alignment_group.add_argument(
        "--align-orientations",
        action="store_true",
        required=False,
        help="Whether to align extracted orientations based on their angles. Allows "
        "for efficient subsequent sampling of cone angles.",
    )
    alignment_group.add_argument(
        "--angles-are-vector",
        action="store_true",
        required=False,
        help="Considers euler_z euler_y, euler_x as vector that will be rotated to align "
        "with the z-axis (1,0,0). Only considered when --align_orientations is set.",
    )
    alignment_group.add_argument(
        "--interpolation-order",
        required=False,
        type=int,
        default=1,
        help="Interpolation order for alignment, less than zero is no interpolation.",
    )
    alignment_group.add_argument(
        "--split-by-micrograph",
        action="store_true",
        required=False,
        help="Create separate output files for each micrograph."
    )

    extraction_group = parser.add_argument_group("Extraction")
    extraction_group.add_argument(
        "--box-size",
        required=True,
        type=int,
        help="Box size for extraction.",
    )
    extraction_group.add_argument(
        "--translation-uncertainty",
        required=False,
        type=int,
        help="Sets box size for extraction to template box plus this value.",
    )
    extraction_group.add_argument(
        "--drop-out-of-box",
        action="store_true",
        required=False,
        help="Whether to drop orientations that fall outside the box. If the "
        "orientations are sensible, it is safe to pass this flag.",
    )

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    data = StarParser(args.orientations, delimiter="\t")
    key = list(data.keys())[0]

    index_map = defaultdict(list)
    for index, value in enumerate(data[key]["_rlnMicrographName"]):
        index_map[value].append(index)

    orientations = Orientations.from_file(args.orientations)
    orientations.translations = np.divide(
        orientations.translations, args.orientations_scaling
    )

    box_size = np.array(args.box_size)
    box_size = np.repeat(box_size, 3 // box_size.size).astype(int)
    extraction_shape = np.copy(box_size)

    if args.align_orientations:
        extraction_shape[:] = int(np.linalg.norm(box_size) + 1)
        for index in range(orientations.rotations.shape[0]):
            rotation_matrix = euler_to_rotationmatrix(orientations.rotations[index])
            rotation_matrix = np.linalg.inv(rotation_matrix)
            if args.angles_are_vector:
                rotation_matrix = align_vectors(
                    orientations.rotations[index], target_vector=(1, 0, 0)
                )
            orientations.rotations[index] = euler_from_rotationmatrix(rotation_matrix)

    ret_orientations, ret_dens, ix = [], [], 0
    n_particles = orientations.translations.shape[0]
    pbar = ProgressBar(message="Processing ", nchars=80, total=n_particles)
    for target_path, indices in index_map.items():

        target = Density.from_file(target_path, use_memmap=True)

        subset = orientations[indices]
        subset, cand_slices, obs_slices = subset.get_extraction_slices(
            target_shape=target.shape,
            extraction_shape=extraction_shape,
            drop_out_of_box=args.drop_out_of_box,
            return_orientations=True,
        )

        dens = Density(
            np.memmap(
                generate_tempfile_name(),
                mode="w+",
                shape=(subset.translations.shape[0], *box_size),
                dtype=np.float32,
            ),
            sampling_rate = (1, *target.sampling_rate),
            metadata = {"batch_dimension" : (0,), "path" : target_path}
        )

        data_subset = np.zeros(extraction_shape, dtype=target.data.dtype)
        for index, (obs_slice, cand_slice) in enumerate(zip(obs_slices, cand_slices)):
            pbar.update(ix + 1)

            data_subset.fill(0)
            data_subset[cand_slice] = target.data[obs_slice]
            target_subset = Density(
                data_subset,
                sampling_rate=target.sampling_rate,
                origin=target.origin,
            )

            if args.align_orientations:
                rotation_matrix = euler_to_rotationmatrix(subset.rotations[index])
                target_subset = target_subset.rigid_transform(
                    rotation_matrix=rotation_matrix,
                    use_geometric_center=True,
                    order=args.interpolation_order,
                )
            target_subset.pad(box_size, center=True)
            dens.data[index] = target_subset.data.astype(np.float32)
            ix += 1

        ret_dens.append(dens)
        ret_orientations.append(subset)

    if not len(ret_dens):
        exit("Found no valid particles.")

    print("")
    if not args.split_by_micrograph:
        ret_orientations = [Orientations(
            translations=np.concatenate([x.translations for x in ret_orientations]),
            rotations=np.concatenate([x.rotations for x in ret_orientations]),
            scores=np.concatenate([x.scores for x in ret_orientations]),
            details=np.concatenate([x.details for x in ret_orientations]),
        )]
        dens_data = Density(
            np.concatenate([x.data for x in ret_dens]),
            sampling_rate=ret_dens[0].sampling_rate
        )
        _ = [unlink(x.data.filename) for x in ret_dens]
        dens_data.metadata.update({"batch_dimension" : (0, )})
        ret_dens = [dens_data]

    for orientation, dens in zip(ret_orientations, ret_dens):
        fname = args.output_prefix
        if args.split_by_micrograph:
            target = splitext(basename(dens.metadata["path"]))[0]
            fname = f"{args.output_prefix}_{target}"

        dens.to_file(f"{fname}.h5")
        orientation.to_file(f"{fname}_aligned.star")
        try:
            unlink(dens.data.filename)
        except Exception:
            continue

if __name__ == "__main__":
    main()
