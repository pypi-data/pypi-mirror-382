"""Minimal sideload helper.

Provides a tiny helper class `x_cls_make_py_mod_sideload_x` with a single
method `run(base_path, module, obj=None)` which loads a module from a file
under `base_path` and returns either the module or a requested attribute.

The implementation is intentionally small to simplify static analysis.
"""

from typing import Any, Optional
import importlib.util
import inspect
import os


class x_cls_make_py_mod_sideload_x:
    def run(
        self, base_path: str, module: str, obj: Optional[str] = None
    ) -> Any:
        """Load a module file under base_path and return module or attribute.

        base_path: directory containing modules or packages
        module: a filename (foo.py), a dotted name (pkg.mod) or a module name
        obj: optional attribute name to return from the module
        """
        if not base_path:
            raise ValueError("base_path must be a non-empty string")

        if not os.path.isdir(base_path) and not os.path.isfile(base_path):
            raise FileNotFoundError(f"base_path does not exist: {base_path}")

        module_file: Optional[str] = None

        # Absolute path to a file
        if os.path.isabs(module) and os.path.isfile(module):
            module_file = module
        # Literal filename relative to base_path
        elif module.endswith(".py"):
            candidate = os.path.join(base_path, module)
            if os.path.isfile(candidate):
                module_file = candidate
        # Dotted path like pkg.mod -> base_path/pkg/mod.py
        elif "." in module:
            parts = module.split(".")
            *pkg, mod = parts
            candidate = os.path.join(base_path, *pkg, f"{mod}.py")
            if os.path.isfile(candidate):
                module_file = candidate
        # Try module.py or package __init__.py
        else:
            candidate = os.path.join(base_path, f"{module}.py")
            if os.path.isfile(candidate):
                module_file = candidate
            else:
                init = os.path.join(base_path, module, "__init__.py")
                if os.path.isfile(init):
                    module_file = init

        if module_file is None:
            raise ImportError(
                f"Cannot resolve module file for module={module} under base_path={base_path}"
            )

        spec = importlib.util.spec_from_file_location(
            f"sideload_{abs(hash(module_file))}", module_file
        )
        if spec is None or spec.loader is None:
            raise ImportError(
                f"Failed to create module spec for {module_file}"
            )

        module_obj = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_obj)

        if obj is None:
            return module_obj

        if not hasattr(module_obj, obj):
            raise AttributeError(
                f"Module loaded from {module_file} has no attribute {obj!r}"
            )

        attr = getattr(module_obj, obj)
        if inspect.isclass(attr):
            return attr()
        return attr


# Packaging-friendly alias
xclsmakepymodsideloadx = x_cls_make_py_mod_sideload_x

__all__ = ["x_cls_make_py_mod_sideload_x", "xclsmakepymodsideloadx"]
