from jinja2 import Environment, PackageLoader, select_autoescape
from faker import Faker
from random import Random
import math
import string


env = Environment(
    loader=PackageLoader("qe_test_gen"),
    variable_start_string="<<",
    variable_end_string=">>",
    trim_blocks=True,
    lstrip_blocks=True,
    autoescape=select_autoescape()
)

template = env.get_template("medical_datamap.jinja2")

states = {
        'California': 118000,
        'Texas': 86030,
        'Florida': 64280, 
        'New York': 62000,
        'Pennsylvania': 37500,
        'Illinois': 38240,
        'Ohio': 35210,
        'Georgia': 31970,
        'North Carolina': 31160,
        'Michigan': 30000,
        'New Jersey': 38000,
        'Virginia': 25760,
        'Washington': 23000,
        'Arizona': 21340,
        'Tennessee': 20620,
        'Massachusetts': 20980,
        'Indiana': 20250,
        'Missouri': 20000,
        'Maryland': 20000,
        'Wisconsin': 17590,
        'Colorado': 17230,
        'Minnesota': 17030,
        'South Carolina': 15280,
        'Alabama': 14990,
        'Louisiana': 13900,
        'Kentucky': 13450,
        'Oregon': 12650,
        'Oklahoma': 11820,
        'Connecticut': 10760,
        'Utah': 9760,
        'Iowa': 9520,
        'Nevada': 9270,
        'Arkansas': 8990,
        'Mississippi': 8840,
        'Kansas': 8770,
        'New Mexico': 6320,
        'Nebraska': 5850,
        'Idaho': 5490,
        'West Virginia': 5350,
        'Hawaii': 4340,
        'New Hampshire': 4110,
        'Maine': 4070,
        'Montana': 3240,
        'Rhode Island': 3280,
        'Delaware': 2950,
        'South Dakota': 2650,
        'North Dakota': 2330,
        'Alaska': 2190,
        'Vermont': 1920,
        'Wyoming': 1720,
}

def make_diagnosis_code():
  sum = 0
  frequency = []
  
  h = 0.0
  for j in range(1, 5001):
    h += 1/(j**2)
  
  for i in range(1, 5001):
    f_i = math.ceil(1000000 * ((i ** -2) / h))
    frequency.append(f_i)
    sum += f_i
  
  if sum > 1000000:
    print(f'Frequency: {frequency[0]} Sum: {sum}')
    frequency[0] = frequency[0] - (sum - 1000000)
  
  rnd = Random()
  rnd.seed(10000)
  diagnosis_code = {}
  for f in frequency:
    gen_fresh_code = lambda: "{}{:0>2}-{:0>2}".format(rnd.choice(string.ascii_uppercase), rnd.randrange(0, 99), rnd.randrange(0, 99))
    fresh_code = gen_fresh_code()
    while fresh_code in diagnosis_code:
      fresh_code = gen_fresh_code()
    diagnosis_code[fresh_code] = f

  return diagnosis_code

def make_credit_cards():
  faker = Faker()
  faker.seed_instance(12345)

  credit_cards = []
  for i in range(0, 100000):
    credit_cards.append(faker.unique.credit_card_number())

  return credit_cards

with open("states.txt", 'w+') as stateFile:
  for key, value in states.items():
    stateFile.write(key + '\n')

diagnosis_code = make_diagnosis_code()
with open("diagnosis_code.txt", 'w+') as diagnosisFile:
  for key, value in diagnosis_code.items():
    diagnosisFile.write(key + '\n')

credit_cards = make_credit_cards()
with open("credit_cards.txt", 'w+') as cardFile:
  for card in credit_cards:
    cardFile.write(card + '\n')


with open("medical.map", 'w+') as mapFile:
  mapFile.write(template.render({'states': states, 'diagnosis_code': diagnosis_code, 'credit_cards': credit_cards} ))
