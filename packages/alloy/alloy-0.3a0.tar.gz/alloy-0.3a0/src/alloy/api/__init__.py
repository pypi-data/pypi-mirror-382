"""
  alloy: Injected module API.
"""

from abc import ABC as Base, abstractmethod
from dataclasses import dataclass

_finalized = False
_modulemap = {}
_cached_values = {}

def _cached_import_polyglot(name: str):
  cached = _cached_values.get(name)
  if cached: return cached
  import polyglot
  value = polyglot.import_value(name)
  _cached_values[name] = value
  return value

@dataclass
class ModuleInterface:

  """ Describes known properties (and visible properties) for a module. """

  keys: {str}
  invisible: {str}

@dataclass
class ModuleInfo:

  """ Record object which holds module info. """

  name: str
  path: [str]
  iface: ModuleInterface

  def __hash__(self):
    return self.name.__hash__()

class ModuleValue(object):

  """ Wraps a value which should be used as a module. """

  def __init__(self, value):
    self.wrapped = value

  def export(self):
    return self.wrapped

  @classmethod
  def polyglot(cls, value):
    return ModuleValue(value)

class SyntheticModule(Base):

  """ Implements a synthetic module interface. """

  def __init__(self, config: ModuleInfo):
    self.info = config

  @abstractmethod
  def interface(self) -> ModuleInterface:
    pass

  @abstractmethod
  def satisfy(self, key: str) -> ModuleValue:
    pass

class ResolvedModule(SyntheticModule):

  """ Implements a synthetic module backed by a value. """

  def __init__(self, interface: ModuleInterface):
    self.iface = interface

  def interface(self) -> ModuleInterface:
    return self.iface

  def satisfy(self, key: str) -> ModuleValue:
    if not _finalized:
      raise RuntimeError("Cannot satisfy synthetic module request: not finalized yet")
    return ModuleValue.polyglot(_cached_import_polyglot(key))

def module_info(name: str, iface: ModuleInterface) -> ModuleInfo:

  """ Create a `ModuleInfo`. """

  return ModuleInfo(name, path = name.split("."), iface = iface)

def module_interface(props: {str}, hidden: {str} = None) -> ModuleInterface:
  return ModuleInterface(
    keys = props,
    invisible = hidden,
  )

def register(config: ModuleInfo, cls):

  """ Register a known module. """

  global _modulemap
  if _finalized:
    raise RuntimeError("Cannot register new injected modules after finalization")
  SyntheticModule.register(cls)
  _modulemap[config] = cls

def modulemap():
  
  """ Return the module map. """

  return _modulemap

def finalize():

  """ Perform final installation. """

  if _finalized:
    raise RuntimeError("Already finalized")
  _finalized = true
  modules = modulemap()
  return modules
