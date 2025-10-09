def add_basic_processing_steps(config):
    config["processing_steps"] = [
        "extract_peaks",
    ]

    return config


def add_abs_quant_is(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("normalize_peaks")

    config["postprocessings"] = ["postprocessing1", "quantification"]
    config["postprocessing1"] = [
        "normalize_peaks",
    ]
    config["quantification"] = ["quantify"]

    return config


def add_abs_quant_no_norm(config):
    config = add_basic_processing_steps(config)

    config["postprocessings"] = ["quantification"]
    config["quantification"] = ["quantify"]
    # The calibration step must use the area_chromatogram column instead of the default normalized_area_chromatogram
    config["calibrate"]["value_col"] = "area_chromatogram"

    return config


def add_rel_quant_no_norm(config):
    config = add_basic_processing_steps(config)

    return config


def add_rel_quant_TIC(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("tic_normalize_peaks")

    config["postprocessings"] = ["postprocessing1"]
    config["postprocessing1"] = [
        "tic_normalize_peaks",
    ]

    return config


def add_rel_quant_PQN(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("pq_normalize_peaks")

    config["postprocessings"] = ["pqn"]
    config["pqn"] = [
        "pq_normalize_peaks",
    ]

    return config


def add_rel_quant_IS(config):
    config = add_basic_processing_steps(config)
    config["processing_steps"].append("normalize_peaks")

    config["postprocessings"] = ["postprocessing1"]
    config["postprocessing1"] = [
        "normalize_peaks",
    ]

    return config


def add_step_to_processing_and_postprocessing(config, step_name):
    config["processing_steps"].append(step_name)

    # Ensure postprocessing structure exists and add the step if not present
    config.setdefault("postprocessings", ["postprocessing1"])
    if "postprocessing1" not in config["postprocessings"]:
        # add as first postprocessing element
        config["postprocessings"].insert(0, "postprocessing1")

    config.setdefault("postprocessing1", [])
    if step_name not in config["postprocessing1"]:
        config["postprocessing1"].append(step_name)

    return config
