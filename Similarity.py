import pandas as pd
from Preprocessing import Preprocessor
from collections import Counter
import CommonMeasures


class TermDocumentMatrix:
    def __init__(self, documents):
        self.preprocessor = Preprocessor()
        self.documents = documents
        self.collection_size = len(documents)
        self.raw_headers, self.column_headers, self.documents_with_occurrences = self.prepare_tdm()

    @property
    def incidence(self):
        df = pd.DataFrame(data=self.documents_with_occurrences.values(),
                          index=self.raw_headers,
                          columns=self.column_headers).fillna(0)

        df = df.loc[:] >= 1
        df.replace(False, 0, inplace=True)
        df.replace(True, 1, inplace=True)
        return df

    @property
    def count(self):
        return pd.DataFrame(data=self.documents_with_occurrences.values(),
                            index=self.raw_headers,
                            columns=self.column_headers).fillna(0)

    @property
    def tf_idf(self):
        def calculate_log_tf_series(series):
            return series.apply(CommonMeasures.log_tf)

        def calculate_idf_series(series):
            return series.apply(lambda a: CommonMeasures.idf(self.collection_size, a))

        df = self.count

        log_tf_df = df.apply(calculate_log_tf_series, axis=1)

        df_series = self.incidence.sum(axis=0)
        idf_series = calculate_idf_series(df_series)

        return log_tf_df.mul(idf_series)

    @property
    def tf_idf_normalized(self):
        tf_idf_df = self.tf_idf
        tf_idf_df.apply(CommonMeasures.normalize, axis=0)
        return tf_idf_df

    def prepare_tdm(self):
        terms = set()
        documents_with_occurrences = {}

        for name, content in self.documents.items():
            preprocessed = self.preprocessor.preprocess(content)
            documents_with_occurrences[name] = Counter(preprocessed)
            terms = terms.union(Counter(preprocessed))

        return self.documents.keys(), terms, documents_with_occurrences

    # Currently supports two documents
    def cosine_similarity(self, d1, d2):
        tf_idf = self.tf_idf_normalized
        s1, s2 = tf_idf.loc[d1], tf_idf.loc[d2]
        return CommonMeasures.dot_product(s1, s2)


if __name__ == '__main__':
    collection = {
        'doc_trump': "Mr. Trump became president after winning the political election. Though he lost the support of "
                     "some republican friends, Trump is friends with President Putin",
        'doc_election': "President Trump says Putin had no political interference is the election outcome. He says it "
                        "was a witchhunt by political parties. He claimed President Putin is a friend who had nothing "
                        "to do with the election",
        'doc_putin': "Post elections, Vladimir Putin became President of Russia. President Putin had served as the "
                     "Prime Minister earlier in his political career"
    }

    tdm = TermDocumentMatrix(collection)
    # print("Term Document Incidence Matrix")
    # print(tdm.incidence)
    # print("Term Document Count Matrix")
    # print(tdm.count)
    # print("Term Document Weight Matrix")
    # print(tdm.tf_idf)
    # print("Term Document (Normalized) Weight Matrix")
    # print(tdm.tf_idf_normalized)
    # print("Cosine Similarity: ")
    print(tdm.cosine_similarity('doc_trump', 'doc_putin'))
