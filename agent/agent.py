from typing import Dict, Any
from .tools import load_events
def answer(query: str) -> Dict[str, Any]:
    df = load_events()
    if df.empty:
        return {'text':'Nog geen events geladen. Run analyse.', 'items':[]}
    q = query.lower()
    # heel simpele filter: toon laatste 10
    items = df.tail(10).to_dict(orient='records')
    return {'text':f'{len(items)} items (demo).', 'items':items}
