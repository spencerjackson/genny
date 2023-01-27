import frequency_map

import re
import math
from jinja2 import Environment, PackageLoader, select_autoescape

DOCUMENT_COUNT=100000

class LoadPhase:
  def __init__(self, env):
    self.env = env

  def context(self):
    return {}

  def generate(self):
    template = self.env.get_template("load_phase.jinja2")
    return template

class UpdatePhase:
  def __init__(self, env, query, update):
    self.env = env
    self.queries =  query
    self.updates = update

  def context(self):
    return {
      'count': len(self.queries) * len(self.updates),
      'queries': self.queries,
      'updates': self.updates
    }

  def generate(self):
    template = self.env.get_template("update_phase.jinja2")
    return template

class PhaseFactory:
  def __init__(self, ex):
    self.ex = ex

    self.freq_map = frequency_map.load_map("maps_pbl.yml")
    self.freq_buckets = {}
    for f in self.freq_map.keys():
      self.freq_buckets[f] = frequency_map.FrequencyBuckets(self.freq_map[f])


  def transformField(selector):
    """Convert a field selector in a query against a field or a set of fields"""
    if selector == "_id":
      return ["_id"]

    # Fixed field
    if selector.startswith("fixed_"):
      return ["field" + selector.replace("fixed_", "")]
  
    if selector.startswith("uar_"):
      uar_re = r"uar_\[(\d),\s*(\d+)\]"
      m = re.match(uar_re, selector)
      assert m is not None
      lower_bound = int(m[1])
      upper_bound = int(m[2])
  
      fields = []
      for i in range(lower_bound, upper_bound + 1):
        fields.append("field" + str(i))
  
      return fields
  
    raise NotImplemented()


  def transformValueSelector(self, field, selector:str):
    """Convert a value selector into a set of values to query"""

    field_num = -1
    fb = None

    if field.startswith("field"):
      field_num = int(field.replace("field", ""))
      fb = self.freq_buckets[field_num]

    if selector == "uar":
      return fb.uar()
    elif selector == "fixed":
      return "49999"
    elif selector.startswith("fixed_"):
      return fb.fixed_bucket(selector.replace("fixed_", ""))
    elif selector.startswith("uar_alllow"):
      return fb.uar_all_low()
    
    raise NotImplemented()

  def parseFieldValue(self, target):
    queryFields = PhaseFactory.transformField(target['field'])
    ret = []
    
    for queryField in queryFields:
      ret.append((queryField,  self.transformValueSelector(queryField, target['value'])))

    return ret

  def makePhases(self, env):
    query = self.parseFieldValue(self.ex['query'])
    update = self.parseFieldValue(self.ex['update'])
    return [LoadPhase(env), UpdatePhase(env, query, update)]

class Workload:
  def __init__(self, env, ex, cf, tc, subExperiment, phaseDescription):
    self.env = env
    self.testName =  f"UpdateOnly-{ex['name']}-{subExperiment}-{cf}-{tc}"
    self.contentionFactor = cf
    self.encryptedFields = ex['encryptedFieldCount']
    self.threadCount = tc
    self.collectionName = ex['coll']
    self.subExperiment = subExperiment

    self.parser = PhaseFactory(phaseDescription)

  def asContext(self):
    phases = self.parser.makePhases(self.env)

    context =  {
      "testName": self.testName,
      "contentionFactor": self.contentionFactor,
      "encryptedFields": self.encryptedFields,
      "threadCount": self.threadCount,
      "collectionName": self.collectionName,
      "iterationsPerThread": math.floor(DOCUMENT_COUNT / self.threadCount),
      "maxPhase": len(phases) - 1,
      "shouldAutoRun": True,
      "phases": phases
    }

    return context
