"""Conservative, image-scoped PPE evidence assessment."""

from core.label_mapping import normalize_detection_label
from core.legal_references import relevant_references

PPE_CLASSES = {
    "helmet": ("helmet", "no_helmet", (0.0, 0.4)),
    "vest": ("vest", "no_vest", (0.1, 0.8)),
    "gloves": ("gloves", "no_gloves", (0.0, 1.0)),
    "boots": ("boots", "no_boots", (0.6, 1.0)),
    "goggles": ("goggles", "no_goggle", (0.0, 0.4)),
}

NOTICE = (
    "Model predictions and spatial associations require human verification. "
    "A photograph cannot establish PPE suitability, legal compliance or site safety."
)
MIN_FLAG_CONFIDENCE = 0.7


def _worker_overlap(item, person, zone):
    x1, y1, x2, y2 = item["bbox"]
    px1, py1, px2, py2 = person["bbox"]
    area = (x2 - x1) * (y2 - y1)
    if area <= 0 or px2 <= px1 or py2 <= py1:
        return 0.0
    intersection = max(0, min(x2, px2) - max(x1, px1)) * max(0, min(y2, py2) - max(y1, py1))
    vertical = ((y1 + y2) / 2 - py1) / (py2 - py1)
    return intersection / area if zone[0] <= vertical <= zone[1] else 0.0


def assess_image(detections, context, class_names):
    """Assess one image against declared site requirements and model evidence."""
    context = context or {}
    supported = {normalize_detection_label(name) for name in class_names}
    requirements = list(dict.fromkeys(context.get("requirements", [])))
    people = [d for d in detections if normalize_detection_label(d.get("label", "")) == "person"]
    workers = [
        {"id": f"Worker {index + 1}", "bbox": person["bbox"], "confidence": person["confidence"],
         "observations": [], "findings": []}
        for index, person in enumerate(people)
    ]
    unassigned = []
    label_to_item = {
        label: (name, zone)
        for name, (positive, negative, zone) in PPE_CLASSES.items()
        for label in (positive, negative)
    }
    for detection in detections:
        normalized_label = normalize_detection_label(detection.get("label", ""))
        item = label_to_item.get(normalized_label)
        if not item:
            continue
        name, zone = item
        overlaps = [_worker_overlap(detection, person, zone) for person in people]
        candidates = [i for i, overlap in enumerate(overlaps) if overlap > 0]
        observation = {**detection, "ppe_item": name, "normalized_label": normalized_label, "source_type": "ai_observation"}
        if len(candidates) == 1 and overlaps[candidates[0]] >= 0.75:
            workers[candidates[0]]["observations"].append(observation)
        else:
            unassigned.append(observation)

    refs = relevant_references(context)
    ppe_refs = [ref["id"] for ref in refs if "ppe" in ref["tags"]]
    for worker, person in zip(workers, people):
        for item in requirements:
            classes = PPE_CLASSES.get(item)
            observations = [obs for obs in worker["observations"] if obs["ppe_item"] == item]
            if not classes or classes[0] not in supported:
                status = "NOT ASSESSABLE"
                reasoning = "The loaded model cannot detect this PPE category."
            elif worker["confidence"] >= MIN_FLAG_CONFIDENCE and any(
                o["normalized_label"] == classes[1] and o["confidence"] >= MIN_FLAG_CONFIDENCE
                for o in observations
            ) and not any(
                o["normalized_label"] == classes[0] for o in observations
            ) and not any(
                o["normalized_label"] == classes[0] and _worker_overlap(o, person, classes[2]) > 0
                for o in unassigned
            ):
                status = "POTENTIAL NON-COMPLIANCE"
                reasoning = (
                    "A model no-PPE prediction was spatially associated with this worker and the user "
                    "declared this item required. This is a potential site-requirement issue, not proof "
                    "of a legal breach; verify the image, association and requirement."
                )
            else:
                status = "REVIEW REQUIRED"
                reasoning = (
                    "Visual evidence does not establish correct use, suitability or compliance. "
                    "An absent or conflicting detection is not proof of missing PPE."
                )
            worker["findings"].append({
                "ppe_item": item,
                "status": status,
                "requirement_source": context.get("requirement_source") or "site_rule",
                "observations": observations,
                "reasoning": reasoning,
                "reference_ids": ppe_refs,
                "recommended_action": "A competent person should verify the image, applicable site requirements and risk controls.",
                "human_verification_required": True,
            })
        statuses = [finding["status"] for finding in worker["findings"]]
        worker["status"] = (
            "POTENTIAL NON-COMPLIANCE" if "POTENTIAL NON-COMPLIANCE" in statuses
            else "REVIEW REQUIRED" if not statuses or "REVIEW REQUIRED" in statuses
            else "NOT ASSESSABLE"
        )
    statuses = [worker["status"] for worker in workers]
    overall = (
        "NOT ASSESSABLE" if not workers else
        "POTENTIAL NON-COMPLIANCE" if "POTENTIAL NON-COMPLIANCE" in statuses else
        "REVIEW REQUIRED" if "REVIEW REQUIRED" in statuses else "NOT ASSESSABLE"
    )
    return {
        "status": overall,
        "workers": workers,
        "unassigned_observations": unassigned,
        "references": refs,
        "context": context,
        "notice": NOTICE,
        "jurisdiction_notice": (
            "Sources are potentially relevant, not a determination of applicability."
            if context.get("jurisdiction") == "great_britain"
            else "Jurisdiction is unknown or outside Great Britain; verify local law before applying sources."
        ),
    }
