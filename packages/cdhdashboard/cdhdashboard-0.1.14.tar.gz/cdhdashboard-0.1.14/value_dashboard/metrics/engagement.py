import traceback

import polars as pl

from value_dashboard.metrics.constants import MODELCONTROLGROUP, INTERACTION_ID, RANK, OUTCOME, ACTION_ID
from value_dashboard.utils.config import get_config
from value_dashboard.utils.py_utils import stable_dedup
from value_dashboard.utils.timer import timed


@timed
def engagement(ih: pl.LazyFrame, config: dict, streaming=False, background=False):
    mand_props_grp_by = stable_dedup(
        config['group_by'] + get_config()["metrics"]["global_filters"] + [MODELCONTROLGROUP])
    negative_model_response = config['negative_model_response']
    positive_model_response = config['positive_model_response']

    if "filter" in config:
        filter_exp_cmp = config["filter"]
        if not isinstance(filter_exp_cmp, str):
            ih = ih.filter(config["filter"])

    try:
        ih_analysis = (
            ih.filter(
                (pl.col(OUTCOME).is_in(negative_model_response + positive_model_response))
            )
            .with_columns([
                pl.when(pl.col(OUTCOME).is_in(positive_model_response)).
                then(1).otherwise(0).alias('Outcome_Binary')
            ])
            .filter(pl.col('Outcome_Binary') == pl.col('Outcome_Binary').max().over(INTERACTION_ID, ACTION_ID, RANK))
            .group_by(mand_props_grp_by)
            .agg([
                pl.len().alias('Count'),
                pl.sum("Outcome_Binary").alias("Positives")
            ])
            .with_columns([
                (pl.col("Count") - (pl.col("Positives"))).alias("Negatives")
            ])
        )
        if background:
            return ih_analysis.collect(background=background, engine="streaming" if streaming else "auto")
        else:
            return ih_analysis
    except Exception as e:
        traceback.print_exc()
        raise e


@timed
def compact_engagement_data(eng_data: pl.DataFrame,
                            config: dict) -> pl.DataFrame:
    grp_by = stable_dedup(config['group_by'] + get_config()["metrics"]["global_filters"])
    data_copy = (
        eng_data
        .group_by(grp_by + [MODELCONTROLGROUP])
        .agg(pl.sum("Negatives").alias("Negatives"),
             pl.sum("Positives").alias("Positives"),
             pl.sum("Count").alias("Count"))
    )

    return data_copy
