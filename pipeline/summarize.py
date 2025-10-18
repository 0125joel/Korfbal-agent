import pandas as pd
def summarize(df: pd.DataFrame) -> dict:
    if df.empty: return {'note':'Geen events'}
    return {'totals': {'rows': int(len(df))}}
