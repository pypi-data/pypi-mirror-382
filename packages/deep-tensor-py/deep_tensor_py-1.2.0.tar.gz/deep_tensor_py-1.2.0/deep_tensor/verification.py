from typing import Sequence


def verify_method(method: str, accepted_methods: Sequence[str]) -> None:
        
    if method in accepted_methods:
        return 
    
    msg = (
        f"Method '{method}' not recognised. Expected one of: " 
        ", ".join(accepted_methods) + "."
    )
    raise ValueError(msg)