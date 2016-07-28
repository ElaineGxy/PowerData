# coding:utf-8
import MySQLdb
import numpy as np
import time


class DBConnect:
    def __init__(self):
        self.db = MySQLdb.connect("192.168.1.58", "dbuser", "lfmysql", "powerloaddata")

    def fetch_data(self, query_sql):
        cursor = self.db.cursor()
        cursor.execute(query_sql)
        results = cursor.fetchall()
        return results

    def close_conn(self):
        self.db.close()


class ProcessData:
    def __init__(self):
        pass

    # normalization data using (x-min)/(max-min)
    def normalize_data_min_min_max(self, data):
        min_value = min(data)
        max_value = max(data)
        return [(float(i) - min_value) / float(max_value - min_value) for i in data]

    # normalization data using (x-mean)/(max-min)
    def normalize_data_mean_min_max(self, data):
        mean_value = np.mean(data)
        min_value = min(data)
        max_value = max(data)
        return [(float(i) - mean_value) / (max_value - min_value) for i in data]

    def normalize_data_z_score(self, data):
        mean_value = np.mean(data)
        s2 = (sum([(i - mean_value) * (i - mean_value) for i in data]) / len(data)) ** 0.5
        return [(i - mean_value) / s2 for i in data]

    def cluster_data(self, data):
        pass


class Cluster:
    def __init__(self):
        pass

    def frechetDistance(self, first, second):
        distance=0.0
        return distance

    # 聚类中心初始化
    def initCentroids(self, dataset, k):
        numSamples, dim = dataset.shape
        centroids = np.zeros(k, dim)
        for i in range(k):
            index = int(np.random.uniform(0, numSamples))
            centroids[i, :] = dataset[index, :]
        return centroids

    def kMean(self, dataset, k):
        numSamples, dim = dataset.shape
        clusterAssment = np.mat(np.zeros(numSamples, 2))
        clusterChanged = True

        ##step1:init centroids
        centroids = self.initCentroids(dataset, k)

        while clusterChanged:
            clusterChanged = False;

            for i in xrange(numSamples):
                minDist = 10000000.0
                minIndex = 0

                for j in range(k):
                    distance = self.frechetDistance(dataset[i, :], centroids[j, :])
                    if distance < minDist:
                        minDist = distance
                        minIndex = j
                # update data jth cluster
                if clusterAssment[i, 0] != minIndex:
                    clusterChanged = True
                    clusterAssment[i, :] = minIndex, minDist * minDist
            # update cluster centroid
            for j in range(k):
                poinsInCluster = dataset[np.nonzero(clusterAssment[:, 0].A == j)[0]]
                centroids[j, :] = np.mean(poinsInCluster, axis=0)

        print "cluster complete!"
        return centroids,clusterAssment

if __name__ == '__main__':
    dbconnect = DBConnect()
    process_data = ProcessData()
    query_sql = "SELECT DISTINCT UserID FROM TemporalData"
    results = dbconnect.fetch_data(query_sql)
    user_ids = []

    for row in results:
        user_ids.append(row[0])

    file = open('noralization_result.txt', 'w')

    for user_id in user_ids:
        query_sql = "SELECT PowerValue FROM TemporalData WHERE UserID=" + str(user_id)
        results = dbconnect.fetch_data(query_sql)
        power_list = []
        for data in results:
            power_list.append(data)
        normalization_data = process_data.normalize_data_z_score(power_list)
        # file.write(str(user_id)+'\n')
        for result in normalization_data:
            file.write("%f\n" % (result))
            # file.write(str(result)+'\n')
    file.close()

    dbconnect.close_conn()
