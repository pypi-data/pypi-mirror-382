import numpy as np


def compute_auc(lst, limit=25, steps=25):
    array = np.array(lst)
    thresholds = np.linspace(0, limit, steps + 1)[1:]
    correct = [np.sum(array < x) for x in thresholds]
    return np.sum(correct) / (len(array) * len(thresholds))


def get_score(item):

    transform = item["transform"]
    pred = transform.apply(item["query_points"])
    refer = item["refer_points"]

    diff_squared = (refer - pred) ** 2
    distances = np.sqrt(np.sum(diff_squared, axis=1))

    return {
        "avg_error": np.mean(distances),
        "max_error": np.max(distances),
        "median_error": np.median(distances),
        "RMSE": np.sqrt(np.mean(diff_squared)),
    }


def validate(items, max_error_limit=50, median_error_limit=20):

    scores = {}
    for name, item in items.items():
        score = get_score(item)
        category = item["category"] if "category" in item else "other"
        inaccurate = (
            score["max_error"] > max_error_limit
            or score["median_error"] > median_error_limit
        )
        scores[name] = {
            "category": category,
            "avg_error": score["avg_error"],
            "max_error": score["max_error"],
            "median_error": score["median_error"],
            "RMSE": score["RMSE"],
            "inaccurate": inaccurate,
        }
    categories = {s["category"] for s in scores.values()}
    aucs = {
        k: compute_auc([v["avg_error"] for v in scores.values() if v["category"] == k])
        for k in categories
    }
    aucs["total"] = compute_auc([v["avg_error"] for v in scores.values()])
    return scores, aucs
