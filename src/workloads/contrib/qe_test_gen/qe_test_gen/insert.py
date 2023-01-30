from workload import Workload, LoadPhase
from jinja2 import Environment, PackageLoader, select_autoescape
import argparse

env = Environment(
    loader=PackageLoader("qe_test_gen"),
    variable_start_string="<<",
    variable_end_string=">>",
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=select_autoescape()
)    

class InsertPhaseFactory:
  def __init__(self, coll):
    self.coll = coll

  def makePhases(self, env):
    return [LoadPhase(env)]

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

  for coll in ["pbl"]:
    for ef in [0, 1, 5, 10]:
      for cf in [1, 4, 8, 16]:
        for tc in [1, 4, 8, 16]:
          testName =  f"InsertOnly-{coll}-{ef}-{cf}-{tc}"
          description = env.from_string(
"""Performs a series of insert operations, using the following properties:
    - All documents have 11 fields, including 1 _id field, and 10 data fields.
    - The first <<encryptedFields>> data fields are encrypted.
    - _id is always unique.
    - Values in data fields fit a '<<collectionName>>' distribution.
    - The insertions are performed by <<threadCount>> client threads.
  This test is uniquely identified as '<<testName>>'.
""")
          workload = Workload(testName, description, coll, env, ef, cf, tc, InsertPhaseFactory(coll))
  
          path = f"{args.destination}/{testName}.yml"
          print(f"Writing {path}")
  
          with open(path, 'w+') as testFile:
            testFile.write(template.render(workload.asContext()))

if __name__== "__main__":
    main()
