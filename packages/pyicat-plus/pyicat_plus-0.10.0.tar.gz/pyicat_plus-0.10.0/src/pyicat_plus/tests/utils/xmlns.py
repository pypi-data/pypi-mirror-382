def strip_xmlns(obj):
    if isinstance(obj, dict):
        return {k: strip_xmlns(v) for k, v in obj.items() if k != "@xmlns"}
    elif isinstance(obj, list):
        return [strip_xmlns(v) for v in obj]
    else:
        return obj
