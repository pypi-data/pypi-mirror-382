from typing import Callable
from dataclasses import dataclass
class ResolverType:
    validate: Callable
    errors: dict
class UseFormType:
    handleSubmit: Callable
    setValue: Callable
    formState: dict
    control: dict
    watch: Callable
    resolver: ResolverType