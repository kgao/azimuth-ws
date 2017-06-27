import json
import copy

import azure.storage.table
import azure.storage.blob


class Settings:
    azure_account = "crispr"
    table_name = "hg38hpcrev1"  # this is also the blob container name
    offtarget_blob_name = "%s/%s/offtargets"


def get_table_service(azure_account):
    try:
        accountkey_file = open('azureTable.apikey', 'r')
    except Exception:
        raise RuntimeError("Unable to find the key to the azure table in azureTable.apikey (file was absent)")
    accountkey = accountkey_file.read().strip()
    accountkey_file.close()
    return azure.storage.table.TableService(account_name=azure_account, account_key=accountkey)


def get_blob_service(azure_account):
    try:
        accountkey_file = open('azureTable.apikey', 'r')
    except Exception:
        raise RuntimeError("Unable to find the key to the azure table in azureTable.apikey (file was absent)")
    accountkey = accountkey_file.read().strip()
    accountkey_file.close()
    return azure.storage.blob.BlockBlobService(account_name=azure_account, account_key=accountkey)


class AzureService(object):

    def __init__(self, verbose=False):
        if verbose:
            print("AZURE VERSION", azure.storage.__version__)
        version = list(map(int, azure.storage.__version__.split(".")))
        if not (version[0] >= 1 or (version[0] == 0 and version[1] >= 34)):
            raise Exception("Detected Azure version < 0.34.0")

        self.columns = ['chromosome', 'start', 'strand', 'offtarget', 'gene', 'score']
        self.table_service = get_table_service(Settings.azure_account)
        self.blob_service = get_blob_service(Settings.azure_account)

    def get_summary(self, gene, sequence):
        """
        :param gene: A gene (e.g. 'ENSG00000141956')
        :param sequence: A sequence belonging to gene (e.g. 'AAAATCTGCCCCCAGCCCTG_GGG')
        :return: a dictionary object with the following keys:
            offTargetListBlob: The offtarget blob name.

            target The guide, with PAM.
            guide: The guide, with PAM.
            azimuth: The (azimuth) guide score.

            tooManyMismatches: Whether mismatch count exceeded mismatch threshold. If True, this result will have an empty blob entry.
            mismatchSiteCount: The number of mismatches found for this guide.
            mismatchDistributionWithPAM: Distribution of mismatches with PAM (with last 3 nt).
            mismatchDistributionWithoutPAM: Distribution of mismatches without PAM (without last 3 nt).

            assumedIntendedTarget: A dictionary with details about the intended target.

            multiplePerfectMatches: ???
            multiplePerfectGenicMatches: ???
            beforeAltStart: ???
            lastExon: ???

        """
        summary = self.table_service.get_entity(Settings.table_name, gene, sequence)
        if not summary['tooManyMismatches']:
            json_keys = 'assumedIntendedTarget', 'mismatchDistributionWithPAM', 'mismatchDistributionWithoutPAM'
            for key in json_keys:
                summary[key] = json.loads(summary[key])
            summary['assumedIntendedTarget'] = dict(zip(*(self.columns, summary['assumedIntendedTarget'])))
        summary.pop('Timestamp')
        summary.pop('etag')
        summary['gene'] = summary.pop('PartitionKey')
        summary['guide'] = "".join(summary.pop('RowKey').split("_"))
        return summary

    def get_offtargets(self, gene, sequence, return_dataframe=False):
        """
        :param gene: A gene (e.g. 'ENSG00000141956')
        :param sequence: A sequence belonging to gene (e.g. 'AAAATCTGCCCCCAGCCCTG_GGG')
        :param return_dataframe: Whether to return a dataframe (requires pandas).
        :return: A list of lists (a table) where each column is ordered and described as follows:
            chromosome: The chromosome number of the offtarget sequence.
            start: The start coordinate of the offtarget sequence.
            strand: The strand of the offtarget sequence (either '+' or '-').
            offtarget: The offtarget sequence.
            gene: The gene to which the offtarget sequence belongs.
            score: The (elevation) offtarget score of the offtarget sequence.
        """
        blob_name = Settings.offtarget_blob_name % (gene, sequence)
        blob_result = self.blob_service.get_blob_to_text(Settings.table_name, blob_name)
        blob_result = json.loads(blob_result.content)
        if return_dataframe:
            import pandas as pd
            df = pd.DataFrame(blob_result, columns=self.columns)
            return df
        return blob_result

    def get_guide(self, gene, sequence, return_dataframe=False):
        return self.get_summary(gene, sequence), self.get_offtargets(gene, sequence, return_dataframe)

    def query_table_gene(self, gene):
        for entity in self.table_service.query_entities(Settings.table_name, filter="PartitionKey eq '%s'" % gene):
            yield entity

    def query_table_sequence(self, seq):
        for entity in self.table_service.query_entities(Settings.table_name, filter="RowKey eq '%s'" % seq):
            yield entity

    def query_table(self, gene, seq):
        return self.table_service.get_entity(Settings.table_name, gene, seq)

    def describe_result(self, data):
        summary, offtargets = data
        summary = copy.copy(summary)
        print("*"*75)
        print(json.dumps(summary, indent=4))
        print("*"*75)
        if isinstance(offtargets, list):
            print("NUM_OFFTARGETS", len(offtargets))
        else:
            print("NUM_OFFTARGETS", offtargets.shape[0])
            if not summary['tooManyMismatches']:
                print(offtargets.iloc[0])
        print("*"*75)

if __name__ == "__main__":
    service = AzureService()
    num_results = 10
    count = 0
    for item in service.query_table_gene('ENSG00000141956'):
        if count >= num_results:
            break
        if item['RowKey'] != "info":
            print("")
            data = service.get_guide(item['PartitionKey'], item['RowKey'], return_dataframe=True)
            service.describe_result(data)
            count += 1

