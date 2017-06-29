from flask import Flask, jsonify, request
import azimuth.model_comparison
import numpy as np
from azure_service import azure_service
from azure_service.azure_service import Settings, AzureService


app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to use Azimuth Web Service API!"

@app.route("/test")
def test():
    sequences = np.array(['ACAGCTGATCTCCAGATATGACCATGGGTT', 'CAGCTGATCTCCAGATATGACCATGGGTTT', 'CCAGAAGTTTGAGCCACAAACCCATGGTCA'])
    amino_acid_cut_positions = np.array([2, 2, 4])
    percent_peptides = np.array([0.18, 0.18, 0.35])
    predictions = azimuth.model_comparison.predict(sequences, amino_acid_cut_positions, percent_peptides)
    for i, prediction in enumerate(predictions):
        print sequences[i], prediction
    return "Hello Azimuth!"

@app.route("/api/v1.0/prediction", methods = ['GET'])
def prediction():
    sequence = request.args.get('sequence')
    # print sequence.split(",")
    result = []
    if sequence is None:
        return jsonify(result)
    # print filter(sequence.split(","))
    filtered_sequence = filter(sequence.split(","))
    if not filtered_sequence:
        return jsonify(result)
    sequences = np.array(filtered_sequence)
    # amino_acid_cut_positions = np.array([1, 1, 2])
    # percent_peptides = np.array([0.18, 0.18, 0.35])
    predictions = azimuth.model_comparison.predict(sequences, None, None)
    for i, prediction in enumerate(predictions):
        # print sequences[i], prediction
        result.append({'Name':sequences[i],'OnTargets':[prediction]})
    return jsonify(result)

@app.route("/api/v1.0/azure/table/summary", methods = ['GET'])
def azure_table_summary():
    gene = request.args.get('gene')
    service = AzureService()
    num_results = 10
    count = 0
    result = []
    for item in service.query_table_gene(gene): # ENSG00000141956 ENSG00000142188
        if count >= num_results:
            break
        if item['RowKey'] != "info":
            # print("")
            # data = service.get_guide(item['PartitionKey'], item['RowKey'], return_dataframe=False)
            data_summary = service.get_summary(item['PartitionKey'], item['RowKey'])
            result.append(data_summary)
            # service.describe_result(data)
            count += 1
    return jsonify(result)

@app.route("/api/v1.0/azure/table/details", methods = ['GET'])
def azure_table_details():
    gene = request.args.get('gene')
    service = AzureService()
    num_results = 10
    count = 0
    result = []
    for item in service.query_table_gene(gene): # ENSG00000141956 ENSG00000142188
        if count >= num_results:
            break
        if item['RowKey'] != "info":
            # print("")
            # data = service.get_guide(item['PartitionKey'], item['RowKey'], return_dataframe=False)
            data_detail = service.get_offtargets(item['PartitionKey'], item['RowKey'], return_dataframe=False)
            result.append(data_detail)
            # service.describe_result(data)
            count += 1
    return jsonify(result)
    
@app.route("/api/v1.0/azure/table/detail", methods = ['GET'])
def azure_table_detail():
    gene = request.args.get('gene')
    sequence = request.args.get('guide')
    service = AzureService()
    num_results = 10
    count = 0
    result = []
    for item in service.query_table_gene(gene): # ENSG00000141956 ENSG00000142188
        if count >= num_results:
            break
        if item['RowKey'] != "info":
            # print("")
            # data = service.get_guide(item['PartitionKey'], item['RowKey'], return_dataframe=False)
            data_detail = service.get_offtargets(item['PartitionKey'], sequence, return_dataframe=False)
            result.append(data_detail)
            # service.describe_result(data)
            count += 1
    return jsonify(result)

# filter out the invalid genome sequences
def filter(arr):
    result = []
    for a in arr:
        if len(a) is 30 and all(c in "ACGT" for c in a):
            result.append(a)
    return result
            


if __name__ == "__main__":
    app.run()