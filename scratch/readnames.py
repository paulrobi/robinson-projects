#https://www.youtube.com/watch?v=q5uM4VKywbA
import csv

with open('names.csv', 'r') as csv_file:
     csv_reader = csv.reader(csv_file)
     next(csv_reader)

     for line in csv_reader:
         print(line[1])
