# -*- coding: UTF-8 -*-
# @Time : 2023/11/15 16:35 
# @Author : 刘洪波
"""
计算相似度的工具
"""
import numpy as np
from typing import Set, List, Tuple
from bigtools import stopwords
from bigtools.jieba_tools import jieba_tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel


def cosine_similarity(vector1: np.array, vector2: np.array):
    """计算两个向量的余弦相似度"""
    return vector1.dot(vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))


class ReturnedTFIDFSimilarities:
    def __init__(self, similarities):
        self.similarities = similarities

    def tolist(self):
        return self.similarities.tolist()

    def argsorted(self, reverse=True):
        if reverse:
            return self.similarities.argsort()[::-1]
        else:
            return self.similarities.argsort()

    def sort(self, reverse=True):
        data = list(enumerate(self.similarities))
        data.sort(key=lambda x: x[1], reverse=reverse)
        return data

    def topk(self, k=10):
        return self.sort()[:k]


class TfidfRetriever:
    def __init__(self, documents: List[str], stop_words: Set[str] = stopwords,
                 ngram_range: Tuple[int, int] = (1, 1), max_features: int = None):
        """
        中文 TF-IDF 检索器
        :param documents: 文档列表
        :param stop_words: 停用词集合
        :param ngram_range: ngram 范围
        :param max_features: 最大特征数
        """
        self.vectorizer = TfidfVectorizer(tokenizer=lambda text: jieba_tokenizer(text, stop_words),
                                          ngram_range=ngram_range, max_features=max_features)
        self.doc_vectors = self.vectorizer.fit_transform(documents)

    def query(self, query: List[str]) -> ReturnedTFIDFSimilarities:
        """
        查询文档相似度
        :param query: 查询文本（str 或 list[str]）
        :return: ReturnedTFIDFSimilarities 对象
        """
        return ReturnedTFIDFSimilarities(self.query_similarity(query))

    def query_similarity(self, query: List[str]):
        """
        查询文档相似度
        :param query: 查询文本（str 或 list[str]）
        :return:
        """
        query_vector = self.vectorizer.transform(query)
        similarities = linear_kernel(query_vector, self.doc_vectors).flatten()
        return similarities

    def query_topk(self, query: List[str], top_k: int = 10):
        """
        查询文档相似度， 返回前top_k个结果
        :param query: 查询文本（str 或 list[str]）
        :param top_k: 返回前 k 个结果（可选）
        :return: ReturnedSimilarities 对象
        """
        return self.query(query).topk(top_k)


def calculate_tfidf_similarity(query: list, documents: list, top_k: int = None, stop_words: Set[str] = stopwords,
                               ngram_range=(1,1), max_features=None):
    """
    中文 TF-IDF 文档检索器，计算TF-IDF相似度
    :param query: 查询语句
    :param documents: 待查询的文本
    :param top_k: 返回前 k 个结果（可选）
    :param stop_words: 停用词
    :param ngram_range: tuple, ngram 范围
    :param max_features: 最大特征数
    :return:
    """
    tf = TfidfRetriever(documents, stop_words, ngram_range, max_features)
    if top_k:
        return tf.query_topk(query, top_k)
    return tf.query(query)
