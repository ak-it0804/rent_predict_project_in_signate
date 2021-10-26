import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geocoder 
import geopy
from geopy.distance import geodesic
import re
import mojimoji
import time
import pickle
# from sklearn.preprocessing import LabelEncoder

def _split_tab(value, key="\t"):
  value_list = str(value).split(key)
  return [value for value in value_list if value != '']

def count_contents(value, key="\t"):
  split_list = value.split(key)
  return len(split_list)

def get_latlng(value):
  value = mojimoji.zen_to_han(value, kana=False)
  dictionary = {"1": "一", "2":"二","3":"三","4":"四","5":"五","6":"六","7":"七","8":"八","9":"九"}
  trans_table = value.maketrans( dictionary)
  value = value.translate(trans_table)
  if value in "丁目":
      value = value.split("丁目")[0] + "丁目"
  # print(value)
  
  g = geocoder.osm(value)
  time.sleep(0.5)
  if g.latlng != None:
      return g.latlng
  else:
      value = value.split("区")[0] + "区"
      g = geocoder.osm(value)
  if g.latlng != None:
      return g.latlng
  else:
      return np.nan


def get_distance(value, base_point = "東京駅"):
  target_latlng = get_latlng(value)
  base_latlng = get_latlng(base_point)
  dis = geodesic(target_latlng, base_latlng).km
  return round(dis,2)

def create_mean_distance_for_station(value, base):
  data_list = _split_tab(value, "\t\t")
  dis_list = [get_latlng(n.split("\t")[1])  for n in data_list]
  print(dis_list)
  dis_list = [get_distance(value=n.split("\t")[1], base_point=base)  for n in data_list]
  dis_list = [dis for dis in dis_list if dis < 20]
  print(dis_list)
  if len(dis_list) == 0:
    return np.nan
  else:
    return np.mean(dis_list) 

def create_facility_count(value):
  facility_list = _split_tab(value)
  
  return len(facility_list)

def get_area(value):
  pattern = "[0-9０-９]+\.[0-9０-９]+"
  result = re.match(pattern, value)
  if result == None:
      return np.nan
  else:
      return float(result.group())

def floor_num(value, f_type=0):
  if type(value) is not str:
    return np.nan
  else:
    pattern = "[0-9０-９]+"
    result = re.findall(pattern, value)
    return int(result[0])

def passed(value):
  value = str(value)
  value = value.replace("新築","0年0ヶ月")
  pattern = "[0-9０-９]+"
  result = re.findall(pattern, value)
  result = int(result[0])*12 + int(result[0])
  return result

def create_datamart(df, col_list):
  datamart = df.copy()
  datamart = datamart.fillna("")
  # datamart["distance_for_tokyo"] = list(map(get_distance,df["所在地"]))
  # datamart = datamart.assign(passed=list(map(get_distance(df["所在地"], base_point="渋谷駅"))))
  # datamart["distance_for_Neighborhood_station"] = list(map(create_mean_distance_for_station,df["アクセス"], df["所在地"]))
  datamart = datamart.assign(passed=list(map(passed, df["築年数"])))
  datamart = datamart.assign(floor_num=list(map(floor_num, df["所在階"])))
  datamart = datamart.assign(area=list(map(get_area, df["面積"])))
  datamart = datamart.assign(facility=list(map(create_facility_count, df["室内設備"])))
  datamart = datamart[col_list]
  print(datamart)
  return datamart

def main():
  col_list = ["passed", "floor_num", "area", "facility"]
  train = pd.read_csv("../data/train.csv", sep=",")
  #train = train.head()
  target = train["賃料"]
  train_feature = train.drop("賃料", axis="columns")
  train_datamart = create_datamart(train_feature, col_list)
  print(train_datamart.head())

  test = pd.read_csv("../data/test.csv", sep=",")
  # test = test.head()
  test_datamart = create_datamart(test, col_list)

  with open('../data/train_data.pickle', 'wb') as train_f:
    pickle.dump(train_datamart , train_f)

  with open('../data/train_target.pickle', 'wb') as train_t:
    pickle.dump(target , train_t)

  with open('../data/test_data.pickle', 'wb') as test_f:
    pickle.dump(test_datamart , test_f)


if __name__ == "__main__":
  main()
