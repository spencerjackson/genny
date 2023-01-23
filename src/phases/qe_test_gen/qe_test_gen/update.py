
import argparse
import math
import re

import frequency_map

"""
Experiment Set u.1: Update unencrypted fields on unencrypted collection
coll = pbl
enc = 0
((ffield, fval), (ufield, uval)) in 
((_id, fixed), (fixed_10, fixed)), 
((fixed_10, fixed_vlf), (fixed_10, uar), 
((uar_[1, 10], uar_alllow), (uar_[1, 10], uar))
cf in {1, 4, 8, 16}
tc in {4, 8, 16}

Experiment Set u.2: Update unecrypted fields on partially encrypted collection
coll = pbl
enc = 5
((ffield, fval), (ufield, uval)) in 
((_id, fixed), (fixed_10, fixed)), 
((fixed_10, fixed_vlf), (fixed_10, uar), 
((uar_[6, 10], uar_alllow), (uar_[6, 10], uar))
cf in {1, 4, 8, 16}
tc in {4, 8, 16}

Experiment Set u.3: Update encrypted fields on partially encrypted collection
coll = pbl
enc = 5
((ffield, fval), (ufield, uval)) in 
((_id, fixed), (fixed_1, fixed)), 
((fixed_1, fixed_vlf), (fixed_1, uar), 
((uar_[1, 5], uar_alllow), (uar_[1, 5], uar))
cf in {1, 4, 8, 16}
tc in {4, 8, 16}

Experiment Set u.4: Update encrypted fields on fully encrypted collection
coll = pbl
enc = 10
((ffield, fval), (ufield, uval)) in 
((_id, fixed), (fixed_1, fixed)), 
((fixed_1, fixed_vlf), (fixed_1, uar), 
((uar_[1, 10], uar_alllow), (uar_[1, 10], uar))
cf in {1, 4, 8, 16}
tc in {4, 8, 16}
"""
from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader("qe_test_gen"),
    variable_start_string="<<",
    variable_end_string=">>",
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=select_autoescape()
)

EXPERIMENTS = [
  {
    # Experiment Set u.1: Update unencrypted fields on unencrypted collection
    "name" : "es1",
    "coll" : "pbl",
    "encryptedFieldCount" : 4,
    "threadCounts" : [4, 8, 16],
    "contentionFactors" : [1,4,8,16],
    "updates" : [
      {
        "query" : {
          "field" : "_id",
          "value" : "fixed"
        },
        "update" : {
          "field" : "fixed_10",
          "value" : "fixed"
        }
      },
      {
        "query": {
          "field": "fixed_10",
          "value": "fixed_vlf"
        },
        "update": {
          "field": "fixed_10",
          "value": "uar",
        },
      },
      {
        "query": {
          "field": "uar_[1,10]",
          "value": "uar_alllow"
        },
        "update": {
          "field": "uar_[1,10]",
          "value": "uar"
        },
      },
    ]
  }
]
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
  def __init__(self, ex, cf, tc, subExperiment, phaseDescription):
    self.testName =  f"UpdateOnly-{ex['name']}-{subExperiment}-{cf}-{tc}"
    self.contentionFactor = cf
    self.encryptedFields = ex['encryptedFieldCount']
    self.threadCount = tc
    self.collectionName = ex['coll']
    self.subExperiment = subExperiment

    self.parser = PhaseFactory(phaseDescription)

  def asContext(self):
    phases = self.parser.makePhases(env)

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
    

template = env.get_template("update_only.jinja2")

def main():
  # type: () -> None
  """Execute Main Entry point."""
  parser = argparse.ArgumentParser(description='MongoDB QE Workload Generator.')

  parser.add_argument('-v', '--verbose', action='count', help="Enable verbose tracing")
  parser.add_argument('-d', '--destination', action='store', default="workload", help="Destination to write workload files")


  args = parser.parse_args()

  if args.verbose:
      logging.basicConfig(level=logging.DEBUG)

  for ex in EXPERIMENTS:
    for subExperiment, phaseDescription in enumerate(ex["updates"]):
      for cf in ex["contentionFactors"]:
        for tc in ex["threadCounts"]:
          workload = Workload(ex, cf, tc, subExperiment, phaseDescription)
  
          path = f"{args.destination}/{workload.testName}.yml"
          print(f"Writing {path}")
  
          with open(path, 'w+') as testFile:
            testFile.write(template.render(workload.asContext()))

if __name__== "__main__":
    main()
