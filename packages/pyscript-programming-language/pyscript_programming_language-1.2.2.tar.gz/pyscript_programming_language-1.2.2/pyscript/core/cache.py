from .singletons import Hook

loading_modules = set()
library = set()
modules = {}

hook = Hook()

del Hook