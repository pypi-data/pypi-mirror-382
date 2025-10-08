from .flagstate import FlagState


def is_turned_on_in_context(flag_state: FlagState,
                            context: dict[str, str] | None) -> bool:
    if not flag_state.is_on:
        return False

    if not context:
        return True

    if len(flag_state.constraints) == 0:
        return True

    # All context keys need to be unconstrained by the flag's constraints
    for key, value in context.items():
        for constraint in flag_state.constraints:
            if key == constraint.key:
                match = False
                for v in constraint.values:
                    if v == value:
                        match = True
                        break
                if not match:
                    return False

    return True
