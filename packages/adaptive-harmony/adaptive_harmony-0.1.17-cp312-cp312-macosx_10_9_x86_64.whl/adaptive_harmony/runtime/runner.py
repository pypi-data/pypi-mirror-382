from pathlib import Path
import sys
import os
import asyncio
import importlib.machinery
import importlib.util
import inspect
import traceback
import types
from typing import Any, Optional
from adaptive_harmony.runtime.data import InputConfig
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

from adaptive_harmony.runtime.context import RecipeConfig, RecipeContext


class RunnerArgs(RecipeConfig, BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ADAPTIVE_", cli_parse_args=True, cli_kebab_case=True)

    recipe_file: Optional[str] = Field(default=None, description="the python recipe file to execute")
    recipe_file_url: Optional[str] = Field(
        default=None, description="Url of recipe in zip format to download and extract to execute"
    )


def main():
    runner_args = RunnerArgs()  # type: ignore
    context = asyncio.run(RecipeContext.from_config(runner_args))
    logger.trace("Loaded config: {}", context.config)
    try:
        if runner_args.recipe_file:
            _load_and_run_recipe(context, runner_args.recipe_file)
        elif runner_args.recipe_file_url:
            recipe_folder = _download_and_extract_recipe(context, runner_args.recipe_file_url)
            _load_and_run_recipe(context, recipe_folder)
        else:
            raise ValueError("recipe_file or recipe_file_url must be provided")
    except Exception as e:
        stack_trace = traceback.format_exc()
        recipe_source = runner_args.recipe_file if runner_args.recipe_file else runner_args.recipe_file_url
        logger.exception(f"Error while running recipe file {recipe_source}", exception=e)
        context.job.report_error(stack_trace)
        sys.exit(1)


def _load_and_run_recipe(context: RecipeContext, recipe_path: str):
    entry = Path(recipe_path).resolve()
    if entry.is_dir():
        entry_file = entry / "main.py"
        if not entry_file.exists():
            raise FileNotFoundError(f"main.py not found in {entry}")
        pkg_dir = entry
        module_name = "main"
    else:
        if entry.suffix != ".py":
            raise ValueError(f"Expected a Python file or directory, got: {entry}")
        entry_file = entry
        pkg_dir = entry.parent
        module_name = entry.stem

    # Create a stable synthetic package name tied to the directory
    synthetic_pkg = f"_adhoc_recipe_{abs(hash(str(pkg_dir))) & 0xFFFFFFFF:x}"

    # Clear any previous loads of this synthetic package in the current process
    for key in list(sys.modules.keys()):
        if key == synthetic_pkg or key.startswith(synthetic_pkg + "."):
            del sys.modules[key]

    # Build a synthetic namespace package pointing at pkg_dir
    pkg_mod = types.ModuleType(synthetic_pkg)
    pkg_mod.__path__ = [str(pkg_dir)]  # allow submodule search in this directory
    pkg_mod.__package__ = synthetic_pkg
    spec_pkg = importlib.machinery.ModuleSpec(synthetic_pkg, loader=None, is_package=True)
    spec_pkg.submodule_search_locations = [str(pkg_dir)]
    pkg_mod.__spec__ = spec_pkg
    sys.modules[synthetic_pkg] = pkg_mod

    # Load the entry file as a submodule of the synthetic package
    fullname = f"{synthetic_pkg}.{module_name}"
    spec = importlib.util.spec_from_file_location(fullname, str(entry_file))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec for {entry_file}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[fullname] = module
    spec.loader.exec_module(module)

    # get recipe_main function
    functions = inspect.getmembers(module, inspect.isfunction)
    recipe_main_functions = [(name, func) for name, func in functions if getattr(func, "is_recipe_main", False)]

    if len(recipe_main_functions) == 0:
        logger.warning("No function annotated with @recipe_main")
        return

    if len(recipe_main_functions) != 1:
        names = [name for (name, _) in recipe_main_functions]
        raise ValueError(f"You must have only one function annotated with @recipe_main. Found {names}")

    (func_name, func) = recipe_main_functions[0]
    logger.trace("Getting recipe function parameters")
    args = _get_params(func, context)

    logger.info(f"Executing recipe function {func_name}")
    if inspect.iscoroutinefunction(func):
        asyncio.run(func(*args))
    else:
        func(*args)
    logger.info(f"Recipe {func_name} completed successfully.")


def _download_and_extract_recipe(context: RecipeContext, file_url: str) -> str:
    import tempfile
    import zipfile

    assert file_url.endswith(".zip"), "Recipe url must point to a zip file"

    # Download the zip file to a temporary location
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp_zip:
        temp_zip_path = temp_zip.name
        context.file_storage.download_locally(file_url, temp_zip_path)

    # Extract to a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="user_recipe")
    with zipfile.ZipFile(temp_zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Clean up the temp zip file
    os.unlink(temp_zip_path)

    recipe_files = [f for f in os.listdir(temp_dir) if f.endswith(".py")]
    if not recipe_files:
        raise FileNotFoundError("No Python recipe file found in the extracted zip")
    main_files = [f for f in recipe_files if f == "main.py"]
    if len(main_files) == 0:
        raise RuntimeError("Recipe zip file must contain a main.py file")

    return temp_dir


def _get_params(func, context: RecipeContext) -> list[Any]:
    args: list[Any] = []
    sig = inspect.signature(func)
    assert len(sig.parameters.items()) <= 2, "Support only functions with 2 parameters or less"

    for _, param in sig.parameters.items():
        # Ensure param.annotation is a type before using issubclass
        if isinstance(param.annotation, type):
            if issubclass(param.annotation, RecipeContext):
                args.append(context)
            elif issubclass(param.annotation, InputConfig):
                if context.config.user_input_file:
                    user_input = param.annotation.load_from_file(context.config.user_input_file)
                else:
                    user_input = param.annotation()
                logger.trace("Loaded user input: {}", user_input)
                args.append(user_input)
        else:
            raise TypeError(f"Parameter '{param.name}' must have a type annotation.")

    return args


if __name__ == "__main__":
    main()
