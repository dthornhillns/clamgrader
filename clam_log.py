import pyodbc

def write_clam(config, target):
    conn = pyodbc.connect(config.sqlConnectString)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Clams(Species, AreaMm, AreaPx, PercentRed) VALUES(%d, %f, %d, %f)" % (target.classification, target.areaSquareMm, target.areaPixel, target.percentRed))
    conn.commit();
