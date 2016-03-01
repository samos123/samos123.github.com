Title: Running Computer Vision algos on Spark with OpenCV
Date: 2016-01-22 16:31
Author: Sam Stoelinga
Category: Big Data
Tags: opencv, spark, tachyon, swift, hadoop, openstack, big data
Slug: computer-vision-opencv-sift-surf-kmeans-on-spark

This post shows several computer vision steps implemented on top of Spark.
OpenCV is used to extract features on top of OpenStack and Spark MLLib KMeans
is used to generate our KMeans dictionary. Then we use Spark and simple vector / matrix
manipulation to do coding and pooling.

Workflow implemented using OpenCV and Spark:

1. Uploading our dataset of images to Hadoop compatible storage as Sequencefile
1. Running OpenCV feature extraction(SURF, SIFT) code using the SequenceFile of images as input
1. Running Spark default K-means model training machine learning code on extracted features
1. Running Feature coding and pooling using our trained K-means model and extracted feature as input
1. (TODO): Running machine learning algortihm to do classification on the encoded features


### Uploading image dataset as SequenceFile to Hadoop compatible storage (Swift)
In the first step we upload our Caltech256 dataset, 30k images totaling 1.2Gb, as SequenceFile to
OpenStack Swift. For this I've created a simplistic command line tool to upload folders containing
files to be stored as a SequenceFile with key=filename and value=raw\_bytes. The tool has been
tested with HDFS and OpenStack Swift.

The following commands show how to download Caltech-256 dataset consisting of JPG images.
Then upload the downloaded images to OpenStack Swift in sequence file format:

    :::bash
    # Download and compile the hadoop sequencefile upload tool
    git clone https://github.com/samos123/hadoop-sequence-file-upload
    cd hadoop-sequence-file-upload
    mvn clean compile assembly:single
    #  Download / extract calltech-256 dataset
    axel http://www.vision.caltech.edu/Image_Datasets/Caltech256/256_ObjectCategories.tar
    tar xf 256_ObjectCategories.tar
    # Upload to Swift, this assumes /etc/hadoop/conf/core-site.xml is used to store Swift details
    ./upload-to-sequence-file.sh 256_ObjectCategories/ swift://spark.swift1/caltech-256.hseq

The dataset is also accessible through Tachyon as we configured it to use Swift as underFS.

### Extract SIFT/SURF features using OpenCV on Spark
I've created a simple Spark application that uses OpenCV
to extract SURF or SIFT features from an image.

    :::python2
    from __future__ import print_function
    import logging
    import io
    import sys
    import os
    
    import cv2
    import numpy as np
    from pyspark import SparkContext
    from pyspark.sql import SQLContext, Row
    
    
    def extract_opencv_features(feature_name):
    
        def extract_opencv_features_nested(imgfile_imgbytes):
            try:
                imgfilename, imgbytes = imgfile_imgbytes
                nparr = np.fromstring(buffer(imgbytes), np.uint8)
                img = cv2.imdecode(nparr, 0)
                if feature_name in ["surf", "SURF"]:
                    extractor = cv2.SURF()
                elif feature_name in ["sift", "SIFT"]:
                    extractor = cv2.SIFT()
    
                kp, descriptors = extractor.detectAndCompute(img, None)
    
                return [(imgfilename, descriptors)]
            except Exception, e:
                logging.exception(e)
                return []
    
        return extract_opencv_features_nested
    
    
    if __name__ == "__main__":
        sc = SparkContext(appName="feature_extractor")
        sqlContext = SQLContext(sc)
    
        try:
            feature_name = sys.argv[1]
            image_seqfile_path = sys.argv[2]
            feature_parquet_path = sys.argv[3]
            partitions = int(sys.argv[4])
        except:
            print("Usage: spark-submit feature_extraction.py <feature_name(sift or surf)> "
                  "<image_sequencefile_input_path> <feature_sequencefile_output_path> <partitions>")
    
        images = sc.sequenceFile(image_seqfile_path, minSplits=partitions)
    
        features = images.flatMap(extract_opencv_features(feature_name))
        features = features.filter(lambda x: x[1] != None)
        features = features.map(lambda x: (Row(fileName=x[0], features=x[1].tolist())))
        featuresSchema = sqlContext.createDataFrame(features)
        featuresSchema.registerTempTable("images")
        featuresSchema.write.parquet(feature_parquet_path)


Using the above Spark application we can start to extract features from our image dataset in Swift.
As input we provide the sequencefile containing `<fileName: String, image: Bytes>`. The extracted
features we write out as parquet file. The following command extracts the sift features from our dataset:

    :::bash
    spark-submit --executor-memory 8g feature_extraction.py sift swift://spark.swift1/caltech-256.hseq swift://spark.swift1/caltech-256-sift1.parquet 100

### K-Means Dictionary generation on SIFT features
We can now generate our dictionary of features through Spark's MLLib KMeans algorithm.
The below application is used to train our KMeans model using the features generated in the
previous step as input dataset.

    :::python2
    from __future__ import print_function
    import io
    import sys
    import os

    import numpy as np
    from pyspark import SparkContext
    from pyspark.mllib.clustering import KMeans
    from pyspark.sql import SQLContext, Row


    if __name__ == "__main__":
        sc = SparkContext(appName="kmeans_dictionary_creation")
        sqlContext = SQLContext(sc)

        try:
            k = int(sys.argv[1])
            feature_parquet_path = sys.argv[2]
            kmeans_model_path = sys.argv[3]
        except:
            print("Usage: spark-submit kmeans.py <k:clusters> "
                  "<feature_sequencefile_input_path> <kmeans_model_output>")

        features = sqlContext.read.parquet(feature_parquet_path)

        # Create same size vectors of the feature descriptors
        # flatMap returns every list item as a new row for the RDD
        # hence transforming x, 128 to x rows of 1, 128 in the RDD.
        # This is needed for KMeans.
        features = features.flatMap(lambda x: x['features']).cache()
        model = KMeans.train(features, k, maxIterations=10, initializationMode="random")

        model.save(sc, kmeans_model_path)
        print("Clusters have been saved as text file to %s" % kmeans_model_path)
        print("Final centers: " + str(model.clusterCenters))
        sc.stop()


Start the spark job with:

    :::bash
    spark-submit --executor-memory 8g kmeans.py 1000 swift://spark.swift1/caltech-256-sift1.parquet swift://spark.swift1/caltech-256-dictionary

### Feature coding and pooling with trained KMeans model
In this step we will use the KMeans dictionary that we trained
in the previous step to encode each point of interest to a single cluster.
This is done by assigning every row of our x * 128 matrix to a single cluster
of the KMeans dictionary. The result is a 1 * k representation for each image
utilizing coding and pooling. For pooling we've implemented a simple max and sum pooling method.

The following Spark application implements feature coding and pooling:

    :::python2
    from __future__ import print_function
    import functools
    import io
    import sys
    import os

    import numpy as np
    from scipy.spatial import distance
    from pyspark.mllib.clustering import KMeansModel
    from pyspark import SparkContext
    from pyspark.sql import SQLContext, Row

    SUPPORTED_POOLING = ["max", "sum"]

    def assign_pooling(row, clusterCenters, pooling):
        image_name = row['fileName']
        feature_matrix = np.array(row['features'])
        clusterCenters = clusterCenters.value
        model = KMeansModel(clusterCenters)
        bow = np.zeros(len(clusterCenters))

        for x in feature_matrix:
            k = model.predict(x)
            dist = distance.euclidean(clusterCenters[k], x)
            if pooling == "max":
                bow[k] = max(bow[k], dist)
            elif pooling == "sum":
                bow[k] = bow[k] + dist

        return Row(fileName=image_name, bow=bow.tolist())


    if __name__ == "__main__":
        sc = SparkContext(appName="kmeans_assign")
        sqlContext = SQLContext(sc)

        try:
            feature_parquet_path = sys.argv[1]
            kmeans_model_path = sys.argv[2]
            bow_parquet_path = sys.argv[3]
            pooling = sys.argv[4]

        except:
            print("Usage: spark-submit feature_coding_pooling.py "
                  "<feature_sequencefile_path> <kmeans_model> "
                  "<bow_sequencefile_path> <pooling_method:max>")

        if pooling not in SUPPORTED_POOLING:
            raise ValueError("Pooling method %s is not supported. Supported poolings methods: %s" % (pooling, SUPPORTED_POOLING))

        features = sqlContext.read.parquet(feature_parquet_path)
        model = KMeansModel.load(sc, kmeans_model_path)
        clusterCenters = model.clusterCenters
        clusterCenters = sc.broadcast(clusterCenters)

        features_bow = features.map(functools.partial(assign_pooling,
            clusterCenters=clusterCenters, pooling=pooling))
        featuresSchema = sqlContext.createDataFrame(features_bow)
        featuresSchema.registerTempTable("images")
        featuresSchema.write.parquet(bow_parquet_path)
        sc.stop()

Execute the spark applicaiton with:

    :::bash
    spark-submit --executor-memory 8g feature_coding_pooling.py swift://spark.swift1/caltech-256-sift1.parquet swift://spark.swift1/caltech-256-dictionary swift://spark.swift1/caltech-256-bow.parquet sum

