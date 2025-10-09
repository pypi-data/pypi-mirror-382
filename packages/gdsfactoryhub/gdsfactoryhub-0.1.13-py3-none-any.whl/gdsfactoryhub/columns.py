"""PostgREST columns definitions."""


def _format(s: str) -> str:
    return s.replace("\n", " ").replace(" ", "").strip()


# Just the columns belonging to each table
PROJECT_COLUMNS = "pk,project_id,description,extraction_rules,eda_layout_file,layer_property_file,created_at"
CELL_COLUMNS = "pk,cell_id,attributes,created_at"
DEVICE_COLUMNS = "pk,device_id,x,y,angle,created_at"
WAFER_COLUMNS = "pk,wafer_id,description,lot_id,attributes,created_at"
DIE_COLUMNS = "pk,x,y,created_at,attributes"
DEVICE_DATA_COLUMNS = "pk,data_type,attributes,acquired_time,data_file,plotting_settings,plot_thumbnail,plot_status,created_at"  # fmt: skip
FUNCTION_COLUMNS = "pk,function_id,version,content,target_model,test_target_model_pk,content,status,function_execution_result,created_at"
ANALYSIS_COLUMNS = "pk,analysis_id,parameters,output,summary_plot,status,failed_function_result,created_at"

# Columns with back-references
PROJECT_COLUMNS_BWD = PROJECT_COLUMNS

CELL_COLUMNS_BWD = _format(f"""
    {CELL_COLUMNS},
    project:projects!inner({PROJECT_COLUMNS_BWD})
""")

DEVICE_COLUMNS_BWD = _format(f"""
    {DEVICE_COLUMNS},
    cell:cells!inner({CELL_COLUMNS_BWD})
""")

WAFER_COLUMNS_BWD = _format(f"""
    {WAFER_COLUMNS},
    project:projects!inner({PROJECT_COLUMNS_BWD})
""")

DIE_COLUMNS_BWD = _format(f"""
    {DIE_COLUMNS},
    wafer:wafers!inner({WAFER_COLUMNS_BWD})
""")

DEVICE_DATA_COLUMNS_BWD = _format(f"""
    {DEVICE_DATA_COLUMNS},
    die:dies({DIE_COLUMNS_BWD}),
    device:devices!inner({DEVICE_COLUMNS_BWD})
""")

FUNCTION_COLUMNS_BWD = FUNCTION_COLUMNS

ANALYSIS_COLUMNS_BWD = _format(f"""
    {ANALYSIS_COLUMNS},
    function:functions!inner({FUNCTION_COLUMNS_BWD}),
    die:dies({DIE_COLUMNS_BWD}),
    wafer:wafers({WAFER_COLUMNS_BWD}),
    device_data({DEVICE_DATA_COLUMNS_BWD})
""")

# Columns with full relationships
PROJECT_COLUMNS_FULL = _format(f"""
    {PROJECT_COLUMNS_BWD},
    wafers({WAFER_COLUMNS}),
    cells({CELL_COLUMNS})
""")

CELL_COLUMNS_FULL = _format(f"""
    {CELL_COLUMNS_BWD},
    devices({DEVICE_COLUMNS})
""")

DEVICE_COLUMNS_FULL = _format(f"""
    {DEVICE_COLUMNS_BWD},
    parent({DEVICE_COLUMNS_BWD}),
    device_data({DEVICE_DATA_COLUMNS})
""")

WAFER_COLUMNS_FULL = _format(f"""
    {WAFER_COLUMNS_BWD},
    dies({DIE_COLUMNS})
""")

DIE_COLUMNS_FULL = _format(f"""
    {DIE_COLUMNS_BWD},
    device_data({DEVICE_DATA_COLUMNS})
""")

DEVICE_DATA_COLUMNS_FULL = _format(f"""
    {DEVICE_DATA_COLUMNS_BWD},
    analyses({ANALYSIS_COLUMNS})
""")

FUNCTION_COLUMNS_FULL = _format(f"""
    {FUNCTION_COLUMNS_BWD},
    analyses({ANALYSIS_COLUMNS})
""")

ANALYSIS_COLUMNS_FULL = ANALYSIS_COLUMNS_BWD
