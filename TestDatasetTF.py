import os
import pandas as pd


class KnowledgeGraph:
    def __init__(self, data_dir):
        # ���ǵ�tf�ĸ���apiʹ�ã�Python���ܽ�Tensor����ֱ��ת�����ַ������ͣ����ǿ��Խ�TF����ת����numpy����
        # ���������ѵ����Ԫ�飬������Ԫ��ȵȣ�����id��Ԫ�飬�������ַ�����Ԫ��
        self.data_dir = data_dir
        self.entity_dict = {}
        self.entities = []
        self.relation_dict = {}
        self.n_entity = 0
        self.n_relation = 0
        self.training_triples = []  # list of triples in the form of (h, t, r)
        self.validation_triples = []
        self.test_triples = []
        self.n_training_triple = 0
        self.n_validation_triple = 0
        self.n_test_triple = 0
        '''load dicts and triples'''
        self.load_dicts()
        self.load_triples()
        '''construct pools after loading'''
        self.training_triple_pool = set(self.training_triples)
        self.golden_triple_pool = set(
            self.training_triples) | set(
            self.validation_triples) | set(
            self.test_triples)

    def load_dicts(self):
        entity_dict_file = 'entity2id.txt'
        relation_dict_file = 'relation2id.txt'
        print('-----Loading entity dict-----')
        entity_df = pd.read_table(
            os.path.join(
                self.data_dir,
                entity_dict_file),
            header=None)
        self.entity_dict = dict(zip(entity_df[0], entity_df[1]))
        self.n_entity = len(self.entity_dict)
        self.entities = list(self.entity_dict.values())
        print('#entity: {}'.format(self.n_entity))
        print('-----Loading relation dict-----')
        relation_df = pd.read_table(
            os.path.join(
                self.data_dir,
                relation_dict_file),
            header=None)
        self.relation_dict = dict(zip(relation_df[0], relation_df[1]))
        self.n_relation = len(self.relation_dict)
        print('#relation: {}'.format(self.n_relation))

    def load_triples(self):
        training_file = 'train.txt'
        validation_file = 'valid.txt'
        test_file = 'test.txt'
        print('-----Loading training triples-----')
        training_df = pd.read_table(
            os.path.join(
                self.data_dir,
                training_file),
            header=None)
        self.training_triples = list(zip([self.entity_dict[h] for h in training_df[0]],
                                         [self.entity_dict[t] for t in training_df[1]],
                                         [self.relation_dict[r] for r in training_df[2]]))
        self.n_training_triple = len(self.training_triples)
        print('#training triple: {}'.format(self.n_training_triple))
        print('-----Loading validation triples-----')
        validation_df = pd.read_table(
            os.path.join(
                self.data_dir,
                validation_file),
            header=None)
        self.validation_triples = list(zip([self.entity_dict[h] for h in validation_df[0]],
                                           [self.entity_dict[t] for t in validation_df[1]],
                                           [self.relation_dict[r] for r in validation_df[2]]))
        self.n_validation_triple = len(self.validation_triples)
        print('#validation triple: {}'.format(self.n_validation_triple))
        print('-----Loading test triples------')
        test_df = pd.read_table(
            os.path.join(
                self.data_dir,
                test_file),
            header=None)
        self.test_triples = list(zip([self.entity_dict[h] for h in test_df[0]],
                                     [self.entity_dict[t] for t in test_df[1]],
                                     [self.relation_dict[r] for r in test_df[2]]))
        self.n_test_triple = len(self.test_triples)
        print('#test triple: {}'.format(self.n_test_triple))