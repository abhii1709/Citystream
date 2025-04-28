CityStream


CityStream is a cloud-native, real-time data pipeline project that streams, processes, stores, analyzes, and visualizes city traffic data — now enhanced with a Machine Learning model to simulate traffic signal timings based on congestion levels and vehicle counts.

Project Overview


CityStream demonstrates the end-to-end flow of real-time data through a modern, scalable, cloud-native architecture:

FastAPI provides an endpoint holding real-time traffic data.

Kafka Producer fetches data from FastAPI and publishes it to Kafka Topics.

Kafka Consumer reads data from topics and stores it into AWS S3 in Parquet format.

AWS Glue catalogs and transforms the raw data.

AWS Athena enables querying on S3 data.

Power BI connects to Athena for real-time visualization.

Machine Learning

Model predicts traffic light durations (green, yellow, red) for different city intersections based on traffic data.

 Tech Stack

 
Backend API: FastAPI

Streaming Platform: Apache Kafka

Cloud Storage: AWS S3

Data Catalog & ETL: AWS Glue

Serverless Query Engine: AWS Athena

Visualization Tool: Power BI

Machine Learning: Scikit-Learn, Pandas

Traffic Simulation UI: Streamlit Dashboard (optional, if you built one)

Message Broker Setup: Kafka + Zookeeper

Containerization: Docker

 Features
Real-time traffic data ingestion using Kafka.

Scalable cloud storage on AWS S3.

Automated data cataloging and querying with AWS Glue and Athena.

Interactive dashboards with Power BI for city-wide traffic monitoring.

Machine Learning model for predicting optimal traffic signal durations based on real-time congestion.

End-to-end cloud-native and modular system.

 Project Architecture

 Machine Learning Model Details


 
Input Features:

Vehicle Count

Congestion Level

Average Speed

Weather Conditions

Target Outputs:

Predicted Green Light Duration (seconds)

Predicted Yellow Light Duration (seconds)

Predicted Red Light Duration (seconds)

Model Type:

Regression models (Random Forest Regressor / Linear Regression)

Use Case:

Simulate adaptive traffic signals that dynamically change based on live traffic conditions to optimize flow and reduce congestion.


 How to Run Locally
Start Zookeeper and Kafka Brokers using Docker.

Run FastAPI server locally to serve data.

Start Kafka Producer to publish real-time traffic data.

Start Kafka Consumer to consume and store data into AWS S3.

Configure AWS Glue for catalog creation.

Query data with AWS Athena.

Train and deploy ML model for traffic signal predictions.

Connect Power BI to Athena for visualizations.

(Optional) Launch Streamlit App for traffic simulation.

 Future Enhancements
Real-time anomaly detection using ML on live Kafka streams.

Use AWS Lambda for serverless microservices.

Integrate alerting system based on congestion spikes.

Incorporate Reinforcement Learning for better traffic light optimization.

Automate entire pipeline with Terraform for IaC (Infrastructure as Code).

Key Highlights
Real-time cloud-native data pipeline.

End-to-end modular architecture.

Integrated ML for predictive simulations.

Serverless and scalable AWS-based backend.

Visualization-ready using Power BI.

Traffic flow optimization through predictive analytics.

 Acknowledgements
FastAPI

Apache Kafka

AWS S3

AWS Glue

AWS Athena

Power BI

Scikit-Learn

Streamlit

 Contact
Feel free to connect for collaboration or any queries!

Developer: Abhishek Choudhary
LinkedIn: https://www.linkedin.com/in/abhishek-c-80b579158/
Email: saysabhii001@gmail.com
