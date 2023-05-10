# -*- coding: utf-8 -*-
import os
import shutil
import jieba
from ase import encrypt, decrypt
from genkey import genkey

inverted_index_mode = True #True or False

def read_K_and_iv_File():
    with open("K.txt", 'rb') as K_file:
        K = K_file.readline()

    with open("iv.txt", 'rb') as iv_file:
        iv = iv_file.readline()
    return (K, iv)


# stop_words list
def stop_words_list():
    stop_words = [line.strip() for line in open("stop_words.txt", encoding='UTF-8').readlines()]
    return stop_words

# depart words
def depart_words(doc):
    doc_depart = jieba.cut_for_search(doc)
    stop_words = stop_words_list()
    out_list = []
    for word in doc_depart:
        if word not in stop_words:
            if word != '\t':
                out_list.append(word)
    return out_list

# inverted_index
def inverted_index(doc_list):
    '''
    input doc_list, return its inverted_index
    :param doc_list: docs' list
    :return: inverted_index, type is dict
    '''
    inverted = {}
    id = 0
    term_list = []
    # inverted index
    for doc in doc_list:
        # depart words
        this_term_list = depart_words(doc)
        # remove duplication
        term_list.extend(this_term_list)
        term_list = list(set(term_list))
        for t in this_term_list:
            if t in inverted:
                if id not in inverted[t]:
                    inverted[t].append(id)
                else:
                    pass
            else:
                inverted[t] = [id]
        id += 1

    return inverted

def forward_index(doc_list):
    index = {}
    id = 0
    term_list = []
    for doc in doc_list:
        # depart words
        this_term_list = depart_words(doc)
        # remove duplication
        term_list.extend(this_term_list)
        term_list = list(set(term_list))
        index[id] = term_list
        id += 1

    return index

def doc_decryption(docs_ID_list, K, iv):
    '''
    decrypt
    :param docs_ID_list:
    :param K:
    :param iv:
    :return: den docs_list
    '''
    en_dir_path = "encryption_docs"
    file_names = os.listdir(en_dir_path)
    docs_list = []
    i = 0
    for fname in file_names:
        if i in docs_ID_list:
            with open(os.path.join('encryption_docs', fname), 'rb') as doc_file:
                en_doc = doc_file.read()
                den_doc = decrypt(en_doc, K, iv).decode('utf-8')
                docs_list.append(den_doc)
        i += 1

    return docs_list


def doc_encryption(docs_path, K, iv):
    file_names = os.listdir(docs_path)
    en_doc_list = []
    for fname in file_names:
        with open(os.path.join(docs_path, fname), 'r') as file:
            doc = file.read()
            en_doc = encrypt(doc, K, iv)
            en_doc_list.append(en_doc)

    for i in range(len(en_doc_list)):
        with open('encryption_docs/en_doc{i}.txt'.format(i=i), 'wb') as en_doc_file:
            en_doc_file.write(en_doc_list[i])


# trapdoor
def build_trapdoor(K, iv, keyword):
    return encrypt(keyword, K, iv)

def build_inverted_index(K, iv, doc_list):
    # build inverted index
    index = inverted_index(doc_list)
    # doc_encryption keywords
    encrypt_index = {}
    for keyword in index.keys():
        encrypt_keyword = build_trapdoor(K, iv, keyword)
        encrypt_index[encrypt_keyword] = index[keyword]

    return encrypt_index

def build_forward_index(K, iv, doc_list):
    index = forward_index(doc_list)
    for id in index.keys():
        encrypt_list = []
        for keyword in index[id]:
            encrypt_keyword = build_trapdoor(K, iv, keyword)
            encrypt_list.append(encrypt_keyword)
        index[id] = encrypt_list
    encrypt_index = index

    return encrypt_index

# doc_encryption
def searchable_encryption(K, iv, docs_path):
    '''
    searchable_encryption
    :param K: masterkey
    :param iv: iv
    :param docs_path: dataset
    :return: encrypt_index
    '''
    # read doc list
    file_names = os.listdir(docs_path)
    doc_list = []
    for fname in file_names:
        with open(os.path.join(docs_path, fname), encoding='utf-8') as doc_file:
            doc_file = doc_file.read().replace("\n", " ")
            doc_list.append(doc_file)

    # build index
    encrypt_idx = {}
    if inverted_index_mode == True:
        encrypt_idx = build_inverted_index(K, iv, doc_list)
    else:
        encrypt_idx = build_forward_index(K, iv, doc_list)

    return encrypt_idx


# search
def search_forward_encrypt_index(docs_ID_list, encrypt_query_keyword, encrypt_index):
    for id in encrypt_index.keys():
        if encrypt_query_keyword in encrypt_index[id]:
            docs_ID_list.append(id)
    return  docs_ID_list

def search_inverted_encrypt_index(docs_ID_list, encrypt_query_keyword, encrypt_index):
    if encrypt_query_keyword in encrypt_index.keys():
        docs_ID_list = encrypt_index[encrypt_query_keyword]
    else:
        assert "no such query_keyword!"
    return docs_ID_list

def search_index(query_keyword, encrypt_index, K, iv):
    '''
    use encrypt_index and trapdoor_key search
    :param query_keyword:
    :param encrypt_index:
    :param K: master key
    :param iv: iv
    :return: docs_ID_list
    '''
    # encrypt query keyword
    encrypt_query_keyword = build_trapdoor(K, iv, query_keyword)
    print("\nquery_keyword: ", query_keyword)
    print("encrypt_query_keyword: ", encrypt_query_keyword)
    # search
    docs_ID_list = []
    if inverted_index_mode == True:
        docs_ID_list = search_inverted_encrypt_index(docs_ID_list, encrypt_query_keyword, encrypt_index)
    else:
        docs_ID_list = search_forward_encrypt_index(docs_ID_list, encrypt_query_keyword, encrypt_index)


    # decrypt
    docs_list = doc_decryption(docs_ID_list, K, iv)
    # write to files
    res_dir = "res"
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)
    else:
        shutil.rmtree(res_dir)
        os.mkdir(res_dir)

    if len(docs_ID_list) != 0:
        i = docs_ID_list[0]
        for doc in docs_list:
            with open(os.path.join(res_dir, "den_doc{i}.txt".format(i=i)), 'w') as res_file:
                res_file.write(doc)
            i += 1
    else:
        print("\nno such result!")

    return docs_ID_list





if __name__ == '__main__':
    # get masterkey
    genkey()
    K, iv = read_K_and_iv_File()
    # encrypt docs
    doc_encryption('docs', K, iv)
    # searchable_encryption
    encrypt_index = searchable_encryption(K, iv, 'docs')
    print("encrypt_index: ")
    print(encrypt_index)

    # query & doc_decryption
    query_key = "deep"
    res_docID_list = search_index(query_key, encrypt_index, K, iv)
    print("\nresult documents' IDs:")
    print(res_docID_list)
    print("\ndone.")