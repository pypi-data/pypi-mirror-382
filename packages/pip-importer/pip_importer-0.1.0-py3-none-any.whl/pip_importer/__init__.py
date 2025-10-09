
def pip_import(module_name, package_names=None):
    import importlib
    try:
        importlib.import_module(module_name)
    except ImportError:
        import pip
        pip.main(["install", *(package_names or [module_name])])
        importlib.import_module(module_name)


__all__ = ["pip_import"]
