from __future__ import annotations

import argparse
import json
import logging
import pickle as pkl
import re
import time
import warnings
from pathlib import Path

import numpy as np
from dbetto.catalog import Props
from lgdo.lh5 import ls
from pygama.pargen.data_cleaning import (
    generate_cut_classifiers,
    get_keys,
)
from pygama.pargen.utils import load_data

from ....utils import (
    build_log,
    convert_dict_np_to_float,
    get_pulser_mask,
)

log = logging.getLogger(__name__)
warnings.filterwarnings(action="ignore", category=RuntimeWarning)


def build_qc(
    config,
    cal_files,
    fft_files,
    table_name,
    overwrite=None,
    pulser_file=None,
    build_plots=False,
):
    search_name = table_name if table_name[-1] == "/" else table_name + "/"

    kwarg_dict_fft = config["fft_fields"]
    kwarg_dict_cal = config["cal_fields"]

    cut_fields = get_keys(
        [key.replace(search_name, "") for key in ls(cal_files[0], search_name)],
        kwarg_dict_cal["cut_parameters"],
    )
    cut_fields += get_keys(
        [key.replace(search_name, "") for key in ls(cal_files[0], search_name)],
        kwarg_dict_fft["cut_parameters"],
    )

    if "initial_cal_cuts" in config:
        init_cal = config["initial_cal_cuts"]
        cut_fields += get_keys(
            [key.replace(search_name, "") for key in ls(cal_files[0], search_name)],
            init_cal["cut_parameters"],
        )

    if len(fft_files) > 0:
        fft_data = load_data(
            fft_files,
            table_name,
            {},
            [*cut_fields, "t_sat_lo", "timestamp", "trapTmax"],
        )

        msg = f"{len(fft_data)} events"
        log.info(msg)

        discharges = fft_data["t_sat_lo"] > 0
        discharge_timestamps = np.where(fft_data["timestamp"][discharges])[0]
        is_recovering = np.full(len(fft_data), False, dtype=bool)
        for tstamp in discharge_timestamps:
            is_recovering = is_recovering | np.where(
                (
                    ((fft_data["timestamp"] - tstamp) < 0.01)
                    & ((fft_data["timestamp"] - tstamp) > 0)
                ),
                True,
                False,
            )
        fft_data["is_recovering"] = is_recovering

        msg = f"{len(fft_data.query('is_recovering'))} discharge recovery events"
        log.info(msg)

        hit_dict_fft = {}
        plot_dict_fft = {}
        cut_data = fft_data.query("is_recovering==0")

        msg = f"cut_data shape: {len(cut_data)}"
        log.debug(msg)

        for name, cut in kwarg_dict_fft["cut_parameters"].items():
            cut_dict, cut_plots = generate_cut_classifiers(
                cut_data,
                {name: cut},
                config.get("rounding", 4),
                display=build_plots,
            )
            hit_dict_fft.update(cut_dict)
            plot_dict_fft.update(cut_plots)

            msg = f"{name} calculated cut_dict is: {json.dumps(convert_dict_np_to_float(cut_dict), indent=2)}"
            log.debug(msg)

            ct_mask = np.full(len(fft_data), True, dtype=bool)
            for outname, info in cut_dict.items():
                # convert to pandas eval
                exp = info["expression"]
                for key in info.get("parameters", None):
                    exp = re.sub(
                        f"(?<![a-zA-Z0-9]){key}(?![a-zA-Z0-9])", f"@{key}", exp
                    )
                fft_data[outname] = fft_data.eval(
                    exp, local_dict=info.get("parameters", None)
                )
                if "_classifier" not in outname:
                    ct_mask = ct_mask & fft_data[outname]
            cut_data = fft_data[ct_mask]

        log.debug("fft cuts applied")
        msg = f"cut_dict is: {json.dumps(convert_dict_np_to_float(hit_dict_fft), indent=2)}"
        log.debug(msg)

    else:
        hit_dict_fft = {}
        plot_dict_fft = {}
        fft_data = None

    if overwrite is not None:
        for name in kwarg_dict_fft["cut_parameters"]:
            for cut_name, cut_dict in overwrite.items():
                if name in cut_name:
                    hit_dict_fft.update({cut_name: cut_dict})

    # load data in
    data, threshold_mask = load_data(
        cal_files,
        table_name,
        {},
        [*cut_fields, "timestamp", "trapTmax", "t_sat_lo"],
        threshold=kwarg_dict_cal.get("threshold", 0),
        return_selection_mask=True,
        cal_energy_param="trapTmax",
    )

    mask = get_pulser_mask(
        pulser_file=pulser_file,
    )

    data["is_pulser"] = mask[threshold_mask]

    msg = f"{len(data.query('~is_pulser'))} non pulser events"
    log.info(msg)

    discharges = data["t_sat_lo"] > 0
    discharge_timestamps = np.where(data["timestamp"][discharges])[0]
    is_recovering = np.full(len(data), False, dtype=bool)
    for tstamp in discharge_timestamps:
        is_recovering = is_recovering | np.where(
            (
                ((data["timestamp"] - tstamp) < 0.01)
                & ((data["timestamp"] - tstamp) > 0)
            ),
            True,
            False,
        )
    data["is_recovering"] = is_recovering

    msg = f"{len(data.query('is_recovering'))} discharge recovery events"
    log.info(msg)

    rng = np.random.default_rng()
    mask = np.full(len(data.query("~is_pulser & ~is_recovering")), False, dtype=bool)
    mask[
        rng.choice(len(data.query("~is_pulser & ~is_recovering")), 4000, replace=False)
    ] = True

    if "initial_cal_cuts" in config:
        init_cal = config["initial_cal_cuts"]
        hit_dict_init_cal, plot_dict_init_cal = generate_cut_classifiers(
            data.query("~is_pulser & ~is_recovering")[mask],
            init_cal["cut_parameters"],
            init_cal.get("rounding", 4),
            display=build_plots,
        )
        ct_mask = np.full(len(data), True, dtype=bool)
        for outname, info in hit_dict_init_cal.items():
            # convert to pandas eval
            exp = info["expression"]
            for key in info.get("parameters", None):
                exp = re.sub(f"(?<![a-zA-Z0-9]){key}(?![a-zA-Z0-9])", f"@{key}", exp)
            data[outname] = data.eval(exp, local_dict=info.get("parameters", None))
            if "classifier" not in outname:
                ct_mask = ct_mask & data[outname]

        mask = mask[ct_mask[(~data["is_pulser"] & ~data["is_recovering"]).to_numpy()]]
        data = data[ct_mask]
        log.debug("initial cal cuts applied")
        msg = f"cut_dict is: {json.dumps(convert_dict_np_to_float(hit_dict_init_cal), indent=2)}"
        log.debug(msg)

    else:
        hit_dict_init_cal = {}
        plot_dict_init_cal = {}

    if len(data.query("~is_pulser & ~is_recovering")) < 500:
        log.info("Less than 500 pulser events")
        cal_data = data.query("~is_pulser & ~is_recovering")
    else:
        cal_data = data.query("~is_pulser & ~is_recovering")[mask]

    hit_dict_cal, plot_dict_cal = generate_cut_classifiers(
        cal_data,
        kwarg_dict_cal["cut_parameters"],
        config.get("rounding", 4),
        display=build_plots,
    )

    if overwrite is not None:
        for name in kwarg_dict_cal["cut_parameters"]:
            for cut_name, cut_dict in overwrite.items():
                if name in cut_name:
                    hit_dict_cal.update({cut_name: cut_dict})

    hit_dict = {**hit_dict_fft, **hit_dict_init_cal, **hit_dict_cal}
    plot_dict = {**plot_dict_fft, **plot_dict_init_cal, **plot_dict_cal}

    for outname, info in hit_dict.items():
        # convert to pandas eval
        exp = info["expression"]
        for key in info.get("parameters", None):
            exp = re.sub(f"(?<![a-zA-Z0-9]){key}(?![a-zA-Z0-9])", f"@{key}", exp)
        if fft_data is not None and outname not in fft_data:
            fft_data[outname] = fft_data.eval(
                exp, local_dict=info.get("parameters", None)
            )
        if outname not in data:
            data[outname] = data.eval(exp, local_dict=info.get("parameters", None))

    qc_results = {}
    for entry in hit_dict:
        if "classifier" not in entry:
            sf_cal = len(data.query(f"{entry}& ~is_pulser & ~is_recovering")) / len(
                data.query("~is_pulser & ~is_recovering")
            )
            sf_cal_err = 100 * np.sqrt(
                ((sf_cal) * (1 - sf_cal))
                / len(data.query("~is_pulser & ~is_recovering"))
            )
            sf_cal *= 100
            msg = f"{entry} cut applied: {sf_cal:.2f}% of events passed the cut for cal data"
            log.info(msg)

            qc_results[entry] = {
                "sf_cal": sf_cal,
                "sf_cal_err": sf_cal_err,
            }

            if fft_data is not None:
                sf_fft = len(fft_data.query(f"{entry} & ~is_recovering")) / len(
                    fft_data.query("~is_recovering")
                )
                sf_fft_err = 100 * np.sqrt(
                    ((sf_fft) * (1 - sf_fft)) / len(fft_data.query("~is_recovering"))
                )
                sf_fft *= 100
                msg = f"{entry} cut applied: {sf_fft:.2f}% of events passed the cut for fft data"

                log.info(msg)

                qc_results[entry].update(
                    {
                        "sf_fft": sf_fft,
                        "sf_fft_err": sf_fft_err,
                    }
                )

    out_dict = convert_dict_np_to_float(
        {"operations": hit_dict, "results": {"qc": qc_results}}
    )

    return out_dict, plot_dict


def par_geds_hit_qc() -> None:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--cal-files", help="cal_files", nargs="*", type=str)
    argparser.add_argument("--fft-files", help="fft_files", nargs="*", type=str)

    argparser.add_argument(
        "--tcm-filelist", help="tcm_filelist", type=str, required=False
    )
    argparser.add_argument(
        "--pulser-file", help="pulser_file", type=str, required=False
    )
    argparser.add_argument(
        "--overwrite-files",
        help="overwrite_files",
        type=str,
        required=False,
        nargs="*",
    )
    argparser.add_argument("--channel", help="channel", type=str)

    argparser.add_argument("--log", help="log_file", type=str)
    argparser.add_argument(
        "--log-config", help="Log config file", type=str, required=False, default={}
    )

    argparser.add_argument(
        "--config-file", help="Config file", type=str, nargs="*", required=True
    )

    argparser.add_argument("--table-name", help="table name", type=str, required=True)

    argparser.add_argument("--plot-path", help="plot_path", type=str, required=False)
    argparser.add_argument("--save-path", help="save_path", type=str)
    args = argparser.parse_args()

    build_log(args.log_config, args.log)

    # get metadata dictionary
    kwarg_dict = Props.read_from(args.config_file)

    if args.overwrite_files:
        overwrite = Props.read_from(args.overwrite_files)
        if args.channel in overwrite:
            overwrite = overwrite[args.channel]["pars"]["operations"]
        else:
            overwrite = None
    else:
        overwrite = None

    if len(args.fft_files) == 1 and Path(args.fft_files[0]).suffix == ".filelist":
        with Path(args.fft_files[0]).open() as f:
            fft_files = f.read().splitlines()
    else:
        fft_files = args.fft_files

    if len(args.cal_files) == 1 and Path(args.cal_files[0]).suffix == ".filelist":
        with Path(args.cal_files[0]).open() as f:
            cal_files = f.read().splitlines()
    else:
        cal_files = args.cal_files

    start = time.time()
    log.info("starting qc")

    out_dict, plot_dict = build_qc(
        config=kwarg_dict,
        cal_files=cal_files,
        fft_files=fft_files,
        table_name=args.table_name,
        overwrite=overwrite,
        pulser_file=args.pulser_file,
        build_plots=int(bool(args.plot_path)),
    )
    msg = f"qc took {time.time() - start:.2f} seconds"
    log.info(msg)

    Path(args.save_path).parent.mkdir(parents=True, exist_ok=True)
    Props.write_to(args.save_path, out_dict)

    if args.plot_path:
        Path(args.plot_path).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.plot_path).open("wb") as f:
            pkl.dump({"qc": plot_dict}, f, protocol=pkl.HIGHEST_PROTOCOL)
