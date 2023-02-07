from workload import Workload, LoadPhase
from jinja2 import Environment, PackageLoader, select_autoescape
import argparse
import re

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

def to_snake_case(camel_case):
  """
  Converts CamelCase to snake_case, useful for generating test IDs
  https://stackoverflow.com/questions/1175208/
  :return: snake_case version of camel_case.
  """
  s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_case)
  s2 = re.sub("-", "_", s1)
  return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s2).lower()

def main():
  # type: () -> None
  """Execute Main Entry point."""
  parser = argparse.ArgumentParser(description='MongoDB QE Workload Generator.')

  parser.add_argument('-v', '--verbose', action='count', help="Enable verbose tracing")
  parser.add_argument('-d', '--destination', action='store', help="Destination to write workload files")
  parser.add_argument('-c', '--patchConfig', action='store', help="Destination to write templated YAML describing how to fetch Genny stats")


  args = parser.parse_args()

  if args.verbose:
      logging.basicConfig(level=logging.DEBUG)

  if not args.destination and not args.patchConfig:
    print("Require one or more request")
    return -1

  testNames = []    

  for coll in ["vlf", "mlf", "lf", "hf", "mhf", "vhf", "blimit", "pbl"]:
    for ef in [0, 1, 5, 10]:
      for cf in [1, 4, 8, 16]:
        for tc in [1, 4, 8, 16]:
          testName =  f"InsertOnly-{coll}-{ef}-{cf}-{tc}"
          testNames.append(to_snake_case(testName))
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
  
          if args.destination:
            with open(path, 'w+') as testFile:
              testFile.write(template.render(workload.asContext()))

  if args.patchConfig:
    template = env.get_template("patch_config.jinja2")

    with open(args.patchConfig, 'w+') as patchConfigFile:
      patchConfigFile.write(template.render({'testNames': testNames}))


if __name__== "__main__":
    main()
