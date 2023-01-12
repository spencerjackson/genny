
import math

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
  def generate(self, env):
    template = env.get_template("load_phase.jinja2")
    return template

class UpdatePhase:
  def generate(self, env):
    template = env.get_template("update_phase.jinja2")
    return template

class WorkloadGenerator:
  def __init__(self, ex, cf, tc):
    self.name = ex['name']
    self.contentionFactor = cf
    self.encryptedFields = ex['encryptedFieldCount']
    self.threadCount = tc
    self.collectionName = ex['coll']

    self.phases = [LoadPhase().generate(env), UpdatePhase().generate(env)]


  def asContext(self):
    return {
      "testName": f"UpdateOnly-{self.name}-{cf}-{tc}",
      "contentionFactor": self.contentionFactor,
      "encryptedFields": self.encryptedFields,
      "threadCount": self.threadCount,
      "collectionName": self.collectionName,
      "iterationsPerThread": math.floor(DOCUMENT_COUNT / self.threadCount),
      "maxPhase": len(self.phases),
      "shouldAutoRun": True,
      "phases": self.phases
    }

template = env.get_template("update_only.jinja2")
for ex in EXPERIMENTS:
    for cf in ex["contentionFactors"]:
        for tc in ex["threadCounts"]:

            #context = {
            #    "testName":  f"UpdateOnly-{ex['name']}-{cf}-{tc}",
            #    "encryptedFields": ex['encryptedFieldCount'],
            #    "threadCount": tc,
            #    "collectionName": ex['coll'],
            #    "iterationsPerThread": math.floor(DOCUMENT_COUNT / tc),
            #    "maxPhase": 2,
            #    "shouldAutoRun": True,
            #    "load": LoadPhase().generate(env),
            #    "phases": [LoadPhase().generate(env), UpdatePhase().generate(env)]
            #}
            workload = WorkloadGenerator(ex, cf, tc)
            print(template.render(workload.asContext()))
