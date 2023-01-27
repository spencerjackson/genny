import argparse

from workload import Workload

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
  },
  {
    #
    "name": "es2",
    "coll": "pbl",
    "encryptedFieldCount" : 10,
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
          "field": "uar_[6,10]",
          "value": "uar_alllow"
        },
        "update": {
          "field": "uar_[6,10]",
          "value": "uar"
        },
      },
    ]
  },
  {
    # Experiment Set u.3: Update encrypted fields on partially encrypted collection
    "name": "es3",
    "coll": "pbl",
    "encryptedFieldCount" : 5,
    "threadCounts" : [4, 8, 16],
    "contentionFactors" : [1,4,8,16],
    "updates" : [
      {
        "query" : {
          "field" : "_id",
          "value" : "fixed"
        },
        "update" : {
          "field" : "fixed_1",
          "value" : "fixed"
        }
      },
      {
        "query": {
          "field": "fixed_1",
          "value": "fixed_vlf"
        },
        "update": {
          "field": "fixed_1",
          "value": "uar",
        },
      },
      {
        "query": {
          "field": "uar_[1,5]",
          "value": "uar_alllow"
        },
        "update": {
          "field": "uar_[1,5]",
          "value": "uar"
        },
      }
    ]
  },
  {
    # Experiment Set u.4: Update encrypted fields on fully encrypted collection
    "name": "es4",
    "coll": "pbl",
    "encryptedFieldCount" : 10,
    "threadCounts" : [4, 8, 16],
    "contentionFactors" : [1,4,8,16],
    "updates" : [
      {
        "query" : {
          "field" : "_id",
          "value" : "fixed"
        },
        "update" : {
          "field" : "fixed_1",
          "value" : "fixed"
        }
      },
      {
        "query": {
          "field": "fixed_1",
          "value": "fixed_vlf"
        },
        "update": {
          "field": "fixed_1",
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
      }
    ]
  },

]
    

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
          workload = Workload(env, ex, cf, tc, subExperiment, phaseDescription)
  
          path = f"{args.destination}/{workload.testName}.yml"
          print(f"Writing {path}")
  
          with open(path, 'w+') as testFile:
            testFile.write(template.render(workload.asContext()))

if __name__== "__main__":
    main()
