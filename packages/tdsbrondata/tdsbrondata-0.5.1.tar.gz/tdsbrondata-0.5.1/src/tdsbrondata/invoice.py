import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tdsbrondata
from pyspark.sql import functions as F
from pyspark.sql.types import *
from delta.tables import DeltaTable

def writeItemList(itemList, itemListPath):
    if DeltaTable.isDeltaTable(tdsbrondata._spark, itemListPath):
        dtItemLists = DeltaTable.forPath(tdsbrondata._spark, itemListPath)
        dfItemLists = dtItemLists.toDF()
        columnsForJoin = ["Dienst", "Source", "FacturatieMaand"]
        itemListKeys = itemList.select(columnsForJoin).dropDuplicates()
        itemListExisting = dfItemLists.join(itemListKeys, on=columnsForJoin, how="left_anti")
        itemListExisting.unionByName(itemList) \
            .write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(itemListPath)
    else:
        itemList.write \
            .format("delta") \
            .mode("overwrite") \
            .option("overwriteSchema", "true") \
            .save(itemListPath)
