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
  value_list = value.split(key)
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
  pattern = "[0-9０-９]+"
  result = re.findall(pattern, value)
  return int(result[0])

def passed(value):
  value = value.replace("新築","0年0ヶ月")
  pattern = "[0-9０-９]+"
  result = re.findall(pattern, value)
  result = int(result[0])*12 + int(result[0])
  return result

def create_datamart(df):
  datamart = df["id"].copy()
  datamart["distance_for_tokyo"] = list(map(get_distance,df["所在地"]))
  # datamart["distance_for_shibuya"] = list(map(get_distance(df["所在地"], base_point="渋谷駅")))
  datamart["distance_for_Neighborhood_station"] = list(map(create_mean_distance_for_station,df["アクセス"], df["所在地"]))
  return datamart

def main():
  train = pd.read_csv("../data/train.csv", sep=",")
  train = train.head()
  target = train["賃料"]
  train_feature = train.drop("賃料", axis="columns")

  datamart = create_datamart(train_feature)

  with open('../data/train_data.pickle', 'wb') as train_f:
    pickle.dump(datamart , train_f)


if __name__ == "__main__":
  main()
