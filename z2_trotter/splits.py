from __future__ import annotations

from typing import Tuple


SPLIT_DESCRIPTIONS = {
    "original": "H_A = H_mass + H_electric; H_B = H_hop",
    "swapped": "H_A = H_hop; H_B = H_mass + H_electric",
    "electric_isolated": "H_A = H_electric; H_B = H_mass + H_hop",
    "mass_isolated": "H_A = H_mass; H_B = H_electric + H_hop",
}


def available_splits() -> Tuple[str, ...]:
    return tuple(SPLIT_DESCRIPTIONS.keys())


def split_description(split_name: str) -> str:
    if split_name not in SPLIT_DESCRIPTIONS:
        allowed = ", ".join(available_splits())
        raise ValueError(f"Unknown split '{split_name}'. Allowed: {allowed}")
    return SPLIT_DESCRIPTIONS[split_name]


def build_split_terms(model, split_name: str):
    if split_name == "original":
        return model.h_mass + model.h_electric, model.h_hop
    if split_name == "swapped":
        return model.h_hop, model.h_mass + model.h_electric
    if split_name == "electric_isolated":
        return model.h_electric, model.h_mass + model.h_hop
    if split_name == "mass_isolated":
        return model.h_mass, model.h_electric + model.h_hop

    allowed = ", ".join(available_splits())
    raise ValueError(f"Unknown split '{split_name}'. Allowed: {allowed}")
