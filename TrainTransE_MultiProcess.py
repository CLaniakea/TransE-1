from random import uniform, sample, choice
import numpy as np
from copy import deepcopy
from multiprocessing import Process, Value, Lock
from multiprocessing.managers import BaseManager
import time


def get_details_of_entityOrRels_list(file_path, split_delimeter="\t"):
    num_of_file = 0
    lyst = []
    with open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            details_and_id = line.strip().split(split_delimeter)
            lyst.append(details_and_id[0])
            num_of_file += 1
    return num_of_file, lyst


def get_details_of_triplets_list(file_path, split_delimeter="\t"):
    num_of_file = 0
    lyst = []
    with open(file_path) as file:
        lines = file.readlines()
        for line in lines:
            triple = line.strip().split(split_delimeter)
            if len(triple) < 3:
                continue
            lyst.append(tuple(triple))
            num_of_file += 1
    return num_of_file, lyst


def norm(lyst):
    # ��һ�� ��λ����
    var = np.linalg.norm(lyst)
    i = 0
    while i < len(lyst):
        lyst[i] = lyst[i] / var
        i += 1
    # ��Ҫ����arrayֵ ��Ϊlist��֧�ּ���
    # return list
    return np.array(lyst)


def dist_L1(h, t, l):
    s = h + l - t
    # �����پ���/���⳵���룬 |x-xi|+|y-yi|ֱ�Ӷ������ĸ���ά��ȡ����ֵ���
    # dist = np.fabs(s).sum()
    return np.fabs(s).sum()


def dist_L2(h, t, l):
    s = h + l - t
    # ŷ�Ͼ���,��������ƽ����δ������һ��Ҫע�⣬��һ����ʽ�;��빫ʽ�Ĵ�����д��������������ʧ��
    # dist = (s * s).sum()
    return (s * s).sum()


class TransE(object):
    def __init__(self, entity_list, rels_list, triplets_list, margin=1, learing_rate=0.01, dim=50, normal_form="L1"):
        self.learning_rate = learing_rate
        self.loss = 0
        self.entity_list = entity_list  # entityList��entity��list����ʼ���󣬱�Ϊ�ֵ䣬key��entity��values����������ʹ��narray����
        self.rels_list = rels_list
        self.triplets_list = triplets_list
        self.margin = margin
        self.dim = dim
        self.normal_form = normal_form
        self.entity_vector_dict = {}
        self.rels_vector_dict = {}
        self.loss_list = []

    def get_loss(self):
        # �ο��廪��Fast-TransX��C++���룬ȷʵ�ٶȺܿ죬Python�ӽ�5��Сʱ��ѵ��C++�����ʮ�����Ӽ�����ɡ����ԵĿ���һ�´��룬
        # ����ԭ���������е�Sbatch�����޸ģ�ֱ�ӽ����ˣ�������Ϊѵ����Ԫ������һ��epoch��Ϊ���batch��ɣ�ÿ��batch��ÿһ����Ԫ�鶼���������������ݶ��½������̲߳�����n��batch��Ӧn���߳�
        # Python������ʷ�������⣬ʹ����GIL��ȫ�ֽ�������ʹ��Python�Ķ��߳̽��Ƽ��ߣ��޷��������cpu�����Կ���ʹ�ö�����Ż�
        # Ϊ��ʹ�ö���̣�ʹ����manager��transE��װΪProxy��������Proxy�����޷���ȡ��װ��TransE������ԣ�������Ҫдget������loss������
        # ����ֵ��ע����ǣ�Python�Ķ�������ܲ�һ������forѭ�������������Ͱ����˽��̵Ĵ��������١��������л������̼���ҪRPCԶ��ͨ�������������������
        # ������trainTransE��trainTransE_MultiProcess�Ա�������trainTransE��forѭ��һ��10����ʱ��8s-9s��trainTransE_MultiProcess��һ��epoch��һ������ʱ��12-13s��
        # ��һ���Ż����������̳أ�ʵ�ֽ��̸��ã���ܣ�tf����
        return self.loss

    def clear_loss(self):
        # �ú���Ҳ��Ϊ��Proxy�����ⲿ����ʧ��0
        self.loss = 0

    def initialize(self):
        """�������еĳ�ʼ���ԼӸĶ�
        ��ʼ��l��e������ԭ����l��e���ļ��е�/m/06rf7�ַ�����ʶת��Ϊ�����dimά��������dimά��������uniform��norm��һ������
        """
        entity_vector_dict, rels_vector_dict = {}, {}
        entity_vector_compo_list, rels_vector_compo_list = [], []
        for item, dict, compo_list, name in zip(
                [self.entity_list, self.rels_list], [entity_vector_dict, rels_vector_dict],
                [entity_vector_compo_list, rels_vector_compo_list], ["entity_vector_dict", "rels_vector_dict"]):
            for entity_or_rel in item:
                n = 0
                compo_list = []
                while n < self.dim:
                    random = uniform(-6 / (self.dim ** 0.5), 6 / (self.dim ** 0.5))
                    compo_list.append(random)
                    n += 1
                compo_list = norm(compo_list)
                dict[entity_or_rel] = compo_list
            print("The " + name + "'s initialization is over. It's number is %d." % len(dict))
        self.entity_vector_dict = entity_vector_dict
        self.rels_vector_dict = rels_vector_dict

    def transE(self, cycle_index=1, num=1500):
        Sbatch = self.sample(num)
        Tbatch = []  # Ԫ��ԣ�ԭ��Ԫ�飬�������Ԫ�飩���б� ��{((h,r,t),(h',r,t'))}
        for sbatch in Sbatch:
            triplets_with_corrupted_triplets = (sbatch, self.get_corrupted_triplets(sbatch))
            if triplets_with_corrupted_triplets not in Tbatch:
                Tbatch.append(triplets_with_corrupted_triplets)
        self.update(Tbatch)

    def sample(self, size):
        return sample(self.triplets_list, size)

    def get_corrupted_triplets(self, triplets):
        '''training triplets with either the head or tail replaced by a random entity (but not both at the same time)
        :param triplet:������h,t,l��
        :return corruptedTriplet:'''
        # i = uniform(-1, 1) if i
        coin = choice([True, False])
        # �������ʱ���(h,t,l)�Ǵ�train�ļ����������ģ�Ҫ�򻵵Ļ�ֱ�����Ѱ��һ����ͷʵ�岻�ȵ�ʵ�弴��
        if coin:  # ��Ӳ�� Ϊ�� ����ͷʵ�壬����һ��
            while True:
                searching_entity = sample(self.entity_vector_dict.keys(), 1)[0]  # ȡ��һ��Ԫ������Ϊsample���ص���һ���б�����
                if searching_entity != triplets[0]:
                    break
            corrupted_triplets = (searching_entity, triplets[1], triplets[2])
        else:  # ��֮������βʵ�壬���ڶ���
            while True:
                searching_entity = sample(self.entity_vector_dict.keys(), 1)[0]
                if searching_entity != triplets[1]:
                    break
            corrupted_triplets = (triplets[0], searching_entity, triplets[2])
        return corrupted_triplets

    def update(self, Tbatch):
        entity_vector_copy = deepcopy(self.entity_vector_dict)
        rels_vector_copy = deepcopy(self.rels_vector_dict)

        for triplets_with_corrupted_triplets in Tbatch:
            head_entity_vector = entity_vector_copy[triplets_with_corrupted_triplets[0][0]]
            tail_entity_vector = entity_vector_copy[triplets_with_corrupted_triplets[0][1]]
            relation_vector = rels_vector_copy[triplets_with_corrupted_triplets[0][2]]

            head_entity_vector_with_corrupted_triplets = entity_vector_copy[triplets_with_corrupted_triplets[1][0]]
            tail_entity_vector_with_corrupted_triplets = entity_vector_copy[triplets_with_corrupted_triplets[1][1]]

            head_entity_vector_before_batch = self.entity_vector_dict[triplets_with_corrupted_triplets[0][0]]
            tail_entity_vector_before_batch = self.entity_vector_dict[triplets_with_corrupted_triplets[0][1]]
            relation_vector_before_batch = self.rels_vector_dict[triplets_with_corrupted_triplets[0][2]]

            head_entity_vector_with_corrupted_triplets_before_batch = self.entity_vector_dict[
                triplets_with_corrupted_triplets[1][0]]
            tail_entity_vector_with_corrupted_triplets_before_batch = self.entity_vector_dict[
                triplets_with_corrupted_triplets[1][1]]

            if self.normal_form == "L1":
                dist_triplets = dist_L1(head_entity_vector_before_batch, tail_entity_vector_before_batch,
                                        relation_vector_before_batch)
                dist_corrupted_triplets = dist_L1(head_entity_vector_with_corrupted_triplets_before_batch,
                                                  tail_entity_vector_with_corrupted_triplets_before_batch,
                                                  relation_vector_before_batch)
            else:
                dist_triplets = dist_L2(head_entity_vector_before_batch, tail_entity_vector_before_batch,
                                        relation_vector_before_batch)
                dist_corrupted_triplets = dist_L2(head_entity_vector_with_corrupted_triplets_before_batch,
                                                  tail_entity_vector_with_corrupted_triplets_before_batch,
                                                  relation_vector_before_batch)
            eg = self.margin + dist_triplets - dist_corrupted_triplets
            if eg > 0:  # ����0ȡԭֵ��С��0����0.����ҳ��ʧ����margin-based ranking criterion
                self.loss += eg
                temp_positive = 2 * self.learning_rate * (
                        tail_entity_vector_before_batch - head_entity_vector_before_batch - relation_vector_before_batch)
                temp_negative = 2 * self.learning_rate * (
                        tail_entity_vector_with_corrupted_triplets_before_batch - head_entity_vector_with_corrupted_triplets_before_batch - relation_vector_before_batch)
                if self.normal_form == "L1":
                    temp_positive_L1 = [1 if temp_positive[i] >= 0 else -1 for i in range(self.dim)]
                    temp_negative_L1 = [1 if temp_negative[i] >= 0 else -1 for i in range(self.dim)]
                    temp_positive_L1 = [float(f) for f in temp_positive_L1]
                    temp_negative_L1 = [float(f) for f in temp_negative_L1]
                    temp_positive = np.array(temp_positive_L1) * self.learning_rate
                    temp_negative = np.array(temp_negative_L1) * self.learning_rate
                    # temp_positive = norm(temp_positive_L1) * self.learning_rate
                    # temp_negative = norm(temp_negative_L1) * self.learning_rate

                # ����ʧ������5�����������ݶ��½��� ���������sample������
                head_entity_vector += temp_positive
                tail_entity_vector -= temp_positive
                relation_vector = relation_vector + temp_positive - temp_negative
                head_entity_vector_with_corrupted_triplets -= temp_negative
                tail_entity_vector_with_corrupted_triplets += temp_negative

                # ��һ���ղŸ��µ����������ټ���ʱ��
                entity_vector_copy[triplets_with_corrupted_triplets[0][0]] = norm(head_entity_vector)
                entity_vector_copy[triplets_with_corrupted_triplets[0][1]] = norm(tail_entity_vector)
                rels_vector_copy[triplets_with_corrupted_triplets[0][2]] = norm(relation_vector)
                entity_vector_copy[triplets_with_corrupted_triplets[1][0]] = norm(
                    head_entity_vector_with_corrupted_triplets)
                entity_vector_copy[triplets_with_corrupted_triplets[1][1]] = norm(
                    tail_entity_vector_with_corrupted_triplets)

                # self.entity_vector_dict = deepcopy(entity_vector_copy)
                # self.rels_vector_dict = deepcopy(rels_vector_copy)
            self.entity_vector_dict = entity_vector_copy
            self.rels_vector_dict = rels_vector_copy

    def write_vector(self, file_path, option):
        if option.strip().startswith("entit"):
            print("Write entities vetor into file      : {}".format(file_path))
            # dyct = deepcopy(self.entity_vector_dict)
            dyct = self.entity_vector_dict
        if option.strip().startswith("rel"):
            print("Write relationships vector into file: {}".format(file_path))
            # dyct = deepcopy(self.rels_vector_dict)
            dyct = self.rels_vector_dict
        with open(file_path, 'w') as file:  # д�ļ���ÿ�θ���д ��with�Զ�����close
            for dyct_key in dyct.keys():
                file.write(dyct_key + "\t")
                file.write(str(dyct[dyct_key].tolist()))
                file.write("\n")

    def write_loss(self, file_path, num_of_col):
        with open(file_path, 'w') as file:
            lyst = deepcopy(self.loss_list)
            for i in range(len(lyst)):
                if num_of_col == 1:
                    # ����4λС��
                    file.write(str(int(lyst[i] * 10000) / 10000) + "\n")
                    # file.write(str(lyst[i]).split('.')[0] + '.' + str(lyst[i]).split('.')[1][:4] + "\n")
                else:
                    # file.write(str(lyst[i]).split('.')[0] + '.' + str(lyst[i]).split('.')[1][:4] + "\t")
                    file.write(str(int(lyst[i] * 10000) / 10000) + "    ")
                    if (i + 1) % num_of_col == 0 and i != 0:
                        file.write("\n")


class MyManager(BaseManager):
    pass


def Manager2():
    m = MyManager()
    m.start()
    return m


MyManager.register('TransE', TransE)


def func1(em, lock, num):
    with lock:
        em.transE(num=num)


if __name__ == "__main__":
    entity_file_path = "data/FB15k/entity2id.txt"
    num_of_entity, entity_list = get_details_of_entityOrRels_list(entity_file_path)
    rels_file_path = "data/FB15k/relation2id.txt"
    num_of_rels, rels_list = get_details_of_entityOrRels_list(rels_file_path)
    train_file_path = "data/FB15k/train.txt"
    num_of_triplets, triplets_list = get_details_of_triplets_list(train_file_path)

    manager = Manager2()

    transE = manager.TransE(entity_list, rels_list, triplets_list, margin=1, dim=50)
    print("\nTransE is initializing...")
    transE.initialize()
    print("\n********** Start TransE training **********")

    for i in range(20000):  # epoch�Ĵ���
        start_time = time.time()
        lock = Lock()
        proces = [Process(target=func1, args=(transE, lock, 1500)) for j in range(10)]
        for p in proces:
            p.start()
        for p in proces:
            p.join()
        print("The loss is %.4f" % transE.get_loss())
        transE.clear_loss()
        end_time = time.time()
        print("The %d epoch(10 batches) takes %.2f ms.\n" % (i, (end_time - start_time) * 1000))
    # transE.transE(100000)
    print("********** End TransE training ***********\n")
    # ѵ�������β���һ����100�����������������µ�����д���ļ�
    transE.write_vector("data/entityVector.txt", "entity")
    transE.write_vector("data/relationVector.txt", "relationship")
    transE.write_loss("data/lossList_25cols.txt", 25)
    transE.write_loss("data/lossList_1cols.txt", 1)