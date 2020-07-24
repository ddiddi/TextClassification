import csv
import matplotlib.pyplot as plt

# Using strategy to see if work sequences are recurring in names for Male vs Female
# def gender_word_break_dict(data):
#   total_words = 0
#   name_dict = {}
#   for name in data:
#     total_words += 1
#     tracker = 0
#     gap = 4
#     while (tracker < len(name)):
#       end = min(len(name), tracker+gap)
#       chunk = name[tracker:end]  
#       if chunk in name_dict:
#         val = name_dict[chunk]
#         name_dict[chunk] = val + 1
#       else:
#         name_dict[chunk] = 1
#       tracker += gap
#   return total_words, name_dict

# Probability distribution based on character probability differences between M vs F
def gender_char_dict(data):
  total_gender_chars = 0
  char_dict = {}
  for name in data:
    for c in name:
      # To give different weightage based on order in name 
      # if c == name[0]:
      #   adder = 50
      # elif c in name[1:3]:
      #   adder = 10
      # else:
      adder = 1
      total_gender_chars += 1
      if c in char_dict.keys():
        val = char_dict[c]
        char_dict[c] = val + adder
      else:
        char_dict[c] = adder
  return total_gender_chars, char_dict

train_male = []
train_female = []
test_data = []

# Reading data from csv
with open('allnames.tsv', 'r', encoding="utf-8") as tsvfile:
  reader = csv.DictReader(tsvfile, dialect='excel-tab')
  for row in reader:
    gender = row['Gender']
    name = row['Person Name'].lower()
    test_train = row['Train/Test']

    # Test Train split
    if test_train == 'Train':
      if gender == 'Male':
        train_male.append(name)
      else:
        train_female.append(name)
    else:
      test_data.append([name, gender])

# To calculate length related disparity in names 
# def avg_std_length(data):
#   count = []
#   total = 0
#   for name in data:
#     first = name.split(' ')
#     total += 1
#     count.append(len(name))
#   mean = sum(count)/total
#   variance = sum([((x - mean) ** 2) for x in count]) / total
#   stddev = variance ** 0.5
#   print("MEAN: ", mean)
#   print("STD: ", stddev)

# avg_std_length(train_male)
# avg_std_length(train_female)

# Attempt to use names for probability distribution
# total_male_names, male_name_dict = gender_word_break_dict(train_male)
# total_female_names, female_name_dict = gender_word_break_dict(train_female)
# P_name_male = {}
# P_name_female = {}
# name_set = set()
# for c in male_name_dict.keys():
#   P_name_male[c] = male_name_dict[c]/total_male_names
#   name_set.add(c)
# for c in female_name_dict.keys():
#   P_name_female[c] = female_name_dict[c]/total_female_names
#   name_set.add(c)

# To see distribution of names between Male and Female 
# male_keys = [k for k, v in P_name_male.items()][:1000]
# male_vals = [v for k, v in P_name_male.items()][:1000]
# plt.bar(range(len(male_vals)), male_vals, align='center')
# plt.xticks(range(len(male_keys)), male_keys)
# plt.show()


# For naive bayes we know 
# P(gender|specific char) = P(specific char|gender) * P(specific char) / P(gender)

# P(specific char|gender) = number of times character seen in name / total characters in gender 
total_male_chars, male_char_dict = gender_char_dict(train_male)
total_female_chars, female_char_dict = gender_char_dict(train_female)
P_char_male = {}
P_char_female = {}
char_set = set()
for c in male_char_dict.keys():
  P_char_male[c] = male_char_dict[c]/total_male_chars
  char_set.add(c)
for c in female_char_dict.keys():
  P_char_female[c] = female_char_dict[c]/total_female_chars
  char_set.add(c)

# To see distribution of characters between Male and Female 
# plt.bar(range(len(P_char_male)), P_char_male.values(), align='center')
# plt.xticks(range(len(P_char_male)), list(P_char_male.keys()))
# plt.figure()
# plt.bar(range(len(P_char_female)), P_char_female.values(), align='center')
# plt.xticks(range(len(P_char_female)), list(P_char_female.keys()))
# plt.show()


# P(specific char) = number of times character repeated / total characters in training set 
total_chars = total_male_chars + total_female_chars
P_char = {}
for s in char_set:
  if s in male_char_dict.keys():
    male_char_count = male_char_dict[s]
  else:
    male_char_count = 0
    male_char_dict[s] = 0

  if s in female_char_dict.keys():
    female_char_count = female_char_dict[s]
  else:
    female_char_count = 0
    female_char_dict[s] = 0
  P_char[s] = (male_char_count + female_char_count)/total_chars

# P(gender) = number of gender / total people in training set 
total_train = len(train_male) + len(train_female)
P_male = len(train_male)/total_train
P_female = len(train_female)/total_train


TM = 0 # Correctly identified Male
FM = 0 # Incorrectly identified Male
TF = 0 # Correctly identified Female
FF = 0 # Inorrectly identified Female


# P(gender|specific char) = P(specific char|gender) * P(specific char) / P(gender)
for elem in test_data:
  name = elem[0]
  gender = elem[1]
  comb_P_male = 1
  comb_P_female = 1
  # print(name)
  for c in name:
    if c in P_char_male.keys() and c in P_char_female.keys():
      # To create threshold for probabilities
      if P_char_male[c] > 0.01 or P_char_female[c] > 0.01:
        P_male_char = (P_char_male[c] * P_char[c])/P_male
        comb_P_male *= P_male_char 

        P_female_char = (P_char_female[c] * P_char[c])/P_female
        comb_P_female *= P_female_char
      # print(c, P_male_char, P_female_char) # To debug
    elif c in P_char_male.keys() and c not in P_char_female.keys():
      comb_P_male = 1
      comb_P_female = 0
    elif c not in P_char_male.keys() and c in P_char_female.keys():
      comb_P_female = 1
      comb_P_male = 0
    
  if comb_P_male > comb_P_female and gender == 'Male':
    TM += 1
  if comb_P_male > comb_P_female and gender == 'Female':
    FM += 1
  if comb_P_male < comb_P_female and gender == 'Female':
    TF += 1
  if comb_P_male < comb_P_female and gender == 'Male':
    FF += 1

# print("TM: ", TM)
# print("FM: ", FM)
# print("TF: ", TF)
# print("FF: ", FF)
Total = TM+FM+TF+FF
print("Accuracy:", (TM + TF)/Total)


