
import importlib
import pkgutil
import inspect
import threading
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import logging
import concurrent.futures

load_dotenv()
logger = logging.getLogger(__name__)


class Loader:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Loader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "initialized", False):
            return
        self._initComponents()
        self.initialized = True

    def _initComponents(self):
        self.timer = None

    # ----------------------------------------------------------------------
    # PUBLIC: Load Skills (directory or module)
    # ----------------------------------------------------------------------
    def loadSkills(self, source, component=None, useThreading=False, parallel=False):
        """
        Loads skill modules either from a directory or a Python package.
        Automatically detects the source type.
        """
        if useThreading:
            def loader():
                try:
                    if isinstance(source, str) and not os.path.exists(source):
                        self._loadSkillsFromModule(source, component, parallel)
                    else:
                        self._loadSkillsFromDirectory(source, component, parallel)
                except Exception:
                    logger.error(f"Error Loading Skills from {source}:", exc_info=True)

            threading.Thread(target=loader, daemon=True).start()
        else:
            try:
                if isinstance(source, str) and not os.path.exists(source):
                    self._loadSkillsFromModule(source, component, parallel)
                else:
                    self._loadSkillsFromDirectory(source, component, parallel)
            except Exception:
                logger.error(f"Error Loading Skills from {source}:", exc_info=True)

    # ----------------------------------------------------------------------
    # INTERNAL: Load From Python Package
    # ----------------------------------------------------------------------
    def _loadSkillsFromModule(self, source, component=None, parallel=False):
        """
        Loads all modules from a Python package.
        Supports auto-scaled parallel execution.
        """
        component = component if component is not None else []
        src = source.lstrip(".") if source.startswith(".") else source

        try:
            package = importlib.import_module(src)
        except Exception as e:
            logger.error(f"Could not import base package {src}: {e}", exc_info=True)
            return

        prefix = package.__name__ + "."
        moduleInfos = [m for m in pkgutil.iter_modules(package.__path__, prefix) if not m.ispkg]
        totalModules = len(moduleInfos)
        if not totalModules:
            logger.warning(f"No submodules found under package {src}")
            return

        def loadModule(modName):
            try:
                module = importlib.import_module(modName)

                # Instantiate classes
                for _, cls in inspect.getmembers(module, inspect.isclass):
                    if cls.__module__ != modName:
                        continue
                    try:
                        component.append(cls())
                    except Exception:
                        logger.error(f"Failed to instantiate {cls.__name__} in {modName}", exc_info=True)

                # Add module if it defines an ACTION_MAP or public functions
                action_map = getattr(module, "actionMap", None) or getattr(module, "ACTION_MAP", None)
                public_funcs = [
                    fn for name, fn in inspect.getmembers(module, inspect.isfunction)
                    if fn.__module__ == modName and not name.startswith("_")
                ]
                if isinstance(action_map, dict) or public_funcs:
                    component.append(module)

            except Exception as e:
                logger.warning(f"Could not load module {modName}: {e}", exc_info=True)

        # ---------- Auto-Scaling Thread Control ----------
        if parallel:
            cpuCount = os.cpu_count() or 4
            maxThreads = min(totalModules, max(4, cpuCount * 2))
            logger.info(f"Loading {totalModules} submodules from {src} using {maxThreads} threads...")

            with concurrent.futures.ThreadPoolExecutor(max_workers=maxThreads) as executor:
                futures = [executor.submit(loadModule, modName) for _, modName, _ in moduleInfos]
                for f in concurrent.futures.as_completed(futures):
                    try:
                        f.result()
                    except Exception as e:
                        logger.error(f"Thread error: {e}", exc_info=True)
        else:
            for _, modName, _ in moduleInfos:
                loadModule(modName)

    # ----------------------------------------------------------------------
    # INTERNAL: Load From Directory
    # ----------------------------------------------------------------------
    def _loadSkillsFromDirectory(self, source, component=None, parallel=False):
        """
        Loads all .py skill files from a directory.
        Auto-scales parallel threads for optimal load speed.
        """
        component = component if component is not None else []
        src = Path(source)
        if not src.is_dir():
            logger.error(f"Skills directory not found: {src}")
            return

        pyFiles = [
            py for py in src.iterdir()
            if py.is_file() and py.suffix == ".py" and py.name != "__init__.py"
        ]
        if not pyFiles:
            logger.warning(f"No skill files found in {src}")
            return

        def loadFile(py):
            modName = f"_dynamic_{py.stem}"
            try:
                spec = importlib.util.spec_from_file_location(modName, str(py))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                sys.modules[modName] = mod

                # Instantiate classes
                for _, cls in inspect.getmembers(mod, inspect.isclass):
                    if cls.__module__ == modName:
                        try:
                            component.append(cls())
                        except Exception:
                            logger.error(f"Failed to instantiate {cls.__name__} in {py.name}", exc_info=True)

                # Add module if it has its own ACTION_MAP or top-level functions
                action_map = getattr(mod, "actionMap", None) or getattr(mod, "ACTION_MAP", None)
                public_funcs = [
                    fn for name, fn in inspect.getmembers(mod, inspect.isfunction)
                    if fn.__module__ == modName and not name.startswith("_")
                ]
                if isinstance(action_map, dict) or public_funcs:
                    component.append(mod)

            except Exception as e:
                logger.warning(f"Could not load module from {py}: {e}", exc_info=True)

        # ---------- Auto-Scaling Thread Control ----------
        if parallel:
            cpuCount = os.cpu_count() or 4
            totalFiles = len(pyFiles)
            maxThreads = min(totalFiles, max(4, cpuCount * 2))
            logger.info(f"Loading {totalFiles} skill files from {src} using {maxThreads} threads...")

            with concurrent.futures.ThreadPoolExecutor(max_workers=maxThreads) as executor:
                futures = [executor.submit(loadFile, py) for py in pyFiles]
                for f in concurrent.futures.as_completed(futures):
                    try:
                        f.result()
                    except Exception as e:
                        logger.error(f"Thread error: {e}", exc_info=True)
        else:
            for py in pyFiles:
                loadFile(py)


# import importlib
# import pkgutil
# import inspect
# import threading
# import sys
# import os
# import os
# from pathlib import Path
# from dotenv import load_dotenv
# import logging

# load_dotenv()
# logger = logging.getLogger(__name__)


# class Loader:
#     _instance = None
#     _lock = threading.Lock()

#     def __new__(cls, *args, **kwargs):
#         if not cls._instance:
#             with cls._lock:
#                 if not cls._instance:
#                     cls._instance = super(Loader, cls).__new__(cls)
#         return cls._instance

#     def __init__(self):
#         if getattr(self, 'initialized', False):
#             return
#         self._initComponents()
#         self.initialized = True

#     def _initComponents(self):
#         self.timer        = None

#     def loadSkills(self, source, component=None, useThreading=False):
#         if useThreading:
#             def loader():
#                 try:
#                     if isinstance(source, str) and not os.path.exists(source):
#                         self._loadSkillsFromModule(source, component)
#                     else:
#                         self._loadSkillsFromDirectory(source, component)
#                 except Exception as e:
#                     logger.error(f"Error Loading Skills from {source}:", exc_info=True)
#             threading.Thread(target=loader, daemon=True).start()
#         else:
#             try:
#                 if isinstance(source, str) and not os.path.exists(source):
#                     self._loadSkillsFromModule(source, component)
#                 else:
#                     self._loadSkillsFromDirectory(source, component)
#             except Exception as e:
#                 logger.error(f"Error Loading Skills from {source}:", exc_info=True)

#     def _loadSkillsFromModule(self, source, component = None):
#         component = component if component is not None else []
#         src = source.lstrip('.') if source.startswith('.') else source
#         package = importlib.import_module(src)
#         prefix  = package.__name__ + "."

#         for _, modName, ispkg in pkgutil.iter_modules(package.__path__, prefix):
#             if ispkg:
#                 continue
#             try:
#                 module = importlib.import_module(modName)
#             except Exception as e:
#                 logger.warning(f"Could not load module {modName}: {e}", exc_info=True)
#                 continue

#             # 1) instantiate classes as before
#             for _, cls in inspect.getmembers(module, inspect.isclass):
#                 if cls.__module__ != modName:
#                     continue
#                 try:
#                     component.append(cls())
#                 except Exception:
#                     logger.error(f"Failed to instantiate {cls.__name__} in {modName}", exc_info=True)

#             # 2) only treat module as a skill if it has its own ACTION_MAP
#             #    or if it defines its own top‐level functions (not imports)
#             action_map = getattr(module, "actionMap", None) or getattr(module, "ACTION_MAP", None)
#             public_funcs = [
#                 fn for name, fn in inspect.getmembers(module, inspect.isfunction)
#                 if fn.__module__ == modName and not name.startswith("_")
#             ]
#             if isinstance(action_map, dict) or public_funcs:
#                 component.append(module)


#     def _loadSkillsFromDirectory(self, source, component = None):
#         component = component if component is not None else []
#         src = Path(source)
#         if not src.is_dir():
#             logger.error(f"Skills directory not found: {src}")
#             return

#         for py in src.iterdir():
#             if not (py.is_file() and py.suffix == ".py" and py.name != "__init__.py"):
#                 continue

#             modName = f"_dynamic_{py.stem}"
#             try:
#                 spec = importlib.util.spec_from_file_location(modName, str(py))
#                 mod  = importlib.util.module_from_spec(spec)
#                 sys.modules[modName] = mod
#                 spec.loader.exec_module(mod)
#                 #print(f"Loaded skill module: {modName}")
#             except Exception as e:
#                 logger.warning(f"Could not load module from {py}: {e}", exc_info=True)
#                 continue

#             # instantiate classes
#             for _, cls in inspect.getmembers(mod, inspect.isclass):
#                 if cls.__module__ != modName:
#                     continue
#                 try:
#                     component.append(cls())
#                 except Exception:
#                     logger.error(f"Failed to instantiate {cls.__name__} in {py.name}", exc_info=True)

#             # module‐level functions filter by modName
#             action_map = getattr(mod, "actionMap", None) or getattr(mod, "ACTION_MAP", None)
#             public_funcs = [
#                 fn for name, fn in inspect.getmembers(mod, inspect.isfunction)
#                 if fn.__module__ == modName and not name.startswith("_")
#             ]
#             if isinstance(action_map, dict) or public_funcs:
#                 component.append(mod)
#                 #print(f"Loaded skill module: {py.name}")