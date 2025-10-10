PRIVACY_UNIT_BLOCK
PRIVACY_LOSS_BLOCK
OPTIONAL_CSV_BLOCK
# See the OpenDP Library docs for more on Context:
# https://docs.opendp.org/en/OPENDP_V_VERSION/api/user-guide/context/index.html#context:
stats_context = dp.Context.compositor(
    data=pl.scan_csv(CSV_PATH, encoding="utf8-lossy").with_columns(EXTRA_COLUMNS),
    privacy_unit=privacy_unit,
    privacy_loss=privacy_loss,
    split_by_weights=WEIGHTS,
    margins=MARGINS_LIST,
)
