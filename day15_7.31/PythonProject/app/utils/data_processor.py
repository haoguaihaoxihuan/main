import pandas as pd
from io import BytesIO
from app.core.response import BizException

REQUIRED_COLUMNS = [
    "id", "Gender", "Age", "Driving_License", "Region_Code",
    "Previously_Insured", "Vehicle_Age", "Vehicle_Damage",
    "Annual_Premium", "Policy_Sales_Channel", "Vintage", "Response"
]

COLUMN_MAPPING = {
    "id": "id",
    "Gender": "gender",
    "Age": "age",
    "Driving_License": "driving_license",
    "Region_Code": "region_code",
    "Previously_Insured": "previously_insured",
    "Vehicle_Age": "vehicle_age",
    "Vehicle_Damage": "vehicle_damage",
    "Annual_Premium": "annual_premium",
    "Policy_Sales_Channel": "policy_sales_channel",
    "Vintage": "vintage",
    "Response": "response",
}

INT_COLUMNS = {"id", "age", "driving_license", "previously_insured", "vintage", "response"}
FLOAT_COLUMNS = {"annual_premium"}


def parse_excel(file_data: BytesIO):
    valid_rows, quality_report, errors = [], {}, []
    try:
        df = pd.read_excel(file_data, engine="openpyxl")
    except Exception as e:
        raise BizException(2002, f"Excel解析失败: {str(e)}", 400)

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise BizException(2002, f"缺少必要列: {', '.join(missing_cols)}", 400)

    quality_report = {
        "total_rows": len(df),
        "total_cols": len(df.columns),
        "missing_values": {col: int(df[col].isna().sum()) for col in REQUIRED_COLUMNS},
        "duplicates": int(df.duplicated().sum()),
        "dtypes": {col: str(df[col].dtype) for col in REQUIRED_COLUMNS},
    }

    for idx, row in df.iterrows():
        row_errors = []
        row_data = {}
        for orig_col, snake_col in COLUMN_MAPPING.items():
            val = row[orig_col]
            if pd.isna(val):
                row_errors.append(f"{orig_col}为空")
                continue
            if snake_col in INT_COLUMNS:
                try:
                    row_data[snake_col] = int(val)
                except (ValueError, TypeError):
                    row_errors.append(f"{orig_col}类型错误，期望整数")
            elif snake_col in FLOAT_COLUMNS:
                try:
                    row_data[snake_col] = float(val)
                except (ValueError, TypeError):
                    row_errors.append(f"{orig_col}类型错误，期望浮点数")
            else:
                val_str = str(val)
                if isinstance(val, float) and val == int(val) and snake_col in ("region_code", "policy_sales_channel"):
                    val_str = str(int(val))
                row_data[snake_col] = val_str
        if row_errors:
            errors.append({"row": int(idx) + 2, "errors": row_errors})
        else:
            valid_rows.append(row_data)

    return valid_rows, quality_report, errors