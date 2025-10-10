# -*- coding: UTF-8 -*-
# @Time : 2023/11/15 16:35 
# @Author : 刘洪波
"""
计算相似度的工具
"""
import numpy as np
from typing import Set, List, Tuple, Union, Optional
from bigtools.stop_words import stopwords
from bigtools.jieba_tools import jieba_tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import bm25s
from bm25s.tokenization import Tokenized


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


class TfidfChineseRetriever:
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


def calculate_chinese_tfidf_similarity(query: list, documents: list, top_k: int = None, stop_words: Set[str] = stopwords,
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
    tf = TfidfChineseRetriever(documents, stop_words, ngram_range, max_features)
    if top_k:
        return tf.query_topk(query, top_k)
    return tf.query(query)


class BM25ChineseRetriever:
    """
    中文 BM25 检索器
    Based on the paper, BM25S offers the following variants:
        Original (method="robertson")
        ATIRE (method="atire")
        BM25L (method="bm25l")
        BM25+ (method="bm25+")
        Lucene (method="lucene") - default
    """
    def __init__(self, documents: List[str], method: str = "lucene", stop_words: Optional[set] = stopwords):
        """
        初始化中文 BM25 检索器
        :param documents: 文档
        :param method (str): BM25 变体，可选 "robertson", "atire", "bm25l", "bm25+", "lucene"（默认）
        :param stop_words (set, optional): 自定义停用词集合。默认使用内置 stopwords
        """
        self.method = method
        self.stop_words = stop_words
        self.corpus_tokens = self.tokenize(documents)
        self.retriever = bm25s.BM25(method=method)
        self.retriever.index(self.corpus_tokens)

    def tokenize(self, texts: Union[str, List[str]], return_ids: bool = True) -> Union[List[List[str]], Tokenized]:
        """
        对文本进行分词，支持返回 token 列表或 Tokenized 对象（含 vocab）。
        :param texts:  文本列表
        :param return_ids: 是否返回文本的ID
        :return:
        """
        if isinstance(texts, str):
            texts = [texts]

        if not return_ids:
            return [jieba_tokenizer(text, self.stop_words) for text in texts]

        # 构建 token 到 id 的映射
        token_to_index = {}
        corpus_ids = []

        for text in texts:
            tokens = jieba_tokenizer(text, self.stop_words)
            doc_ids = []
            for token in tokens:
                if token not in token_to_index:
                    token_to_index[token] = len(token_to_index)
                doc_ids.append(token_to_index[token])
            corpus_ids.append(doc_ids)

        return Tokenized(ids=corpus_ids, vocab=token_to_index)

    def retrieve(self, queries: Union[str, List[str]], top_k: int = 10) -> List[dict]:
        """
        检索最相关的文档。
        :param queries: 单个查询字符串或查询字符串列表
        :param top_k: 返回 top-k 结果
        :return: List of dicts, each with keys: 'query', 'scores', 'documents'
        """
        if isinstance(queries, str):
            queries = [queries]

        results = []
        for query in queries:
            query_tokens = self.tokenize(query, return_ids=False)
            docs, scores = self.retriever.retrieve(query_tokens, k=top_k)
            results.append({
                "query": query,
                "scores": scores[0].tolist(),
                "documents": docs[0].tolist()
            })
        return results


def calculate_chinese_bm25_similarity(query: list, documents: list, method: str = "lucene",
                                      stop_words: Set[str] = stopwords, top_k: int = 10):
    """
    计算中文 BM25 相似度
    :param query: 查询语句
    :param documents: 待查询的文本
    :param method: BM25 变体，可选 "robertson", "atire", "bm25l", "bm25+", "lucene"（默认）
    :param top_k: 返回前 k 个结果（可选）
    :param stop_words: 停用词
    :return:
    """
    # 初始化类, 构建索引
    retriever = BM25ChineseRetriever(documents=documents, method=method, stop_words=stop_words)
    # 检索
    return retriever.retrieve(query, top_k=top_k)
