from csv import DictReader
from typing import List, Dict

file_handle = open("weather.csv", "r", encoding="utf8")
csv_reader = DictReader(file_handle)
table: List[Dict[str, float]] = []

for row in csv_reader:
    float_row: Dict[str, float] = {}
    for column in row:
        float_row[column] = float(row[column])
    table.append(float_row)
#    print(table)

high_sum: float = 0.0
for row in table:
    high_sum += row["high"]
    print("High temp average: " +str(high_sum / len(table)))



file_handle.close()
