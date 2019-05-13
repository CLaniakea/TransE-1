from numpy import *
import operator


class Test:
    '''���������۹���
��������֪ʶ����һ����n��ʵ�壬��ô���۹������£�
����ÿһ�����Ե���Ԫ��a�е�ͷʵ�����βʵ�壬�����滻Ϊ����֪ʶ���е���������ʵ�壬Ҳ���ǻ����n����Ԫ�顣
�ֱ������n����Ԫ�����������ֵ����transE�У����Ǽ���h+r-t��ֵ���������Եõ�n������ֵ���ֱ��Ӧ����n����Ԫ�顣
������n������ֵ������������
��¼ԭ������Ԫ��a������ֵ��������š�
�����д��ڲ��Լ��еĲ�����Ԫ���ظ��������̡�
ÿ����ȷ��Ԫ�������ֵ�����������ƽ�����õ���ֵ���ǳ�ΪMean Rank��
������ȷ��Ԫ����������������С��10�ı������õ���ֵ���ǳ�ΪHits@10��
�����������۵Ĺ��̣���������ָ�꣺Mean Rank��Hits@10������Mean RankԽСԽ�ã�Hits@10Խ��Խ�á��ô���δ����Hits@10����Python�������ִ��������ٶȺ�����
������ߺ���ʹ���廪��ѧ���Fast_TransX���룬ʹ��C++��д�����ܸߣ��ܹ����ٵó�ѵ���Ͳ��Խ����
'''
    def __init__(self, entity_list, entity_vector_list, relation_list, relation_vector_list, triple_list_train,
                 triple_list_test,
                 label="head", is_fit=False):
        self.entity_list = {}
        self.relation_list = {}
        for name, vec in zip(entity_list, entity_vector_list):
            self.entity_list[name] = vec
        for name, vec in zip(relation_list, relation_vector_list):
            self.relation_list[name] = vec
        self.triple_list_train = triple_list_train
        self.triple_list_test = triple_list_test
        self.rank = []
        self.label = label
        self.is_fit = is_fit

    def write_rank(self, dir):
        print("д��")
        file = open(dir, 'w')
        for r in self.rank:
            file.write(str(r[0]) + "\t")
            file.write(str(r[1]) + "\t")
            file.write(str(r[2]) + "\t")
            file.write(str(r[3]) + "\n")
        file.close()

    def get_rank(self):
        cou = 0
        for triplet in self.triple_list_test:
            rank_list = {}
            for entity_temp in self.entity_list.keys():
                if self.label == "head":
                    corrupted_triplet = (entity_temp, triplet[1], triplet[2])
                    if self.is_fit and (corrupted_triplet in self.triple_list_train):
                        continue
                    rank_list[entity_temp] = distance(self.entity_list[entity_temp], self.entity_list[triplet[1]],
                                                      self.relation_list[triplet[2]])
                else:  # ���ݱ�ǩ�滻ͷʵ������滻βʵ��������
                    corrupted_triplet = (triplet[0], entity_temp, triplet[2])
                    if self.is_fit and (corrupted_triplet in self.triple_list_train):
                        continue
                    rank_list[entity_temp] = distance(self.entity_list[triplet[0]], self.entity_list[entity_temp],
                                                      self.relation_list[triplet[2]])
            name_rank = sorted(rank_list.items(), key=operator.itemgetter(1))  # ����Ԫ�صĵ�һ���������������
            if self.label == 'head':
                num_tri = 0
            else:
                num_tri = 1
            x = 1
            for i in name_rank:
                if i[0] == triplet[num_tri]:
                    break
                x += 1
            self.rank.append((triplet, triplet[num_tri], name_rank[0][0], x))
            print(x)
            cou += 1
            if cou % 10000 == 0:
                print(cou)

    def get_relation_rank(self):
        cou = 0
        self.rank = []
        for triplet in self.triple_list_test:
            rank_list = {}
            for relation_temp in self.relation_list.keys():
                corrupted_triplet = (triplet[0], triplet[1], relation_temp)
                if self.is_fit and (corrupted_triplet in self.triple_list_train):
                    continue
                rank_list[relation_temp] = distance(self.entity_list[triplet[0]], self.entity_list[triplet[1]],
                                                    self.relation_list[relation_temp])
            name_rank = sorted(rank_list.items(), key=operator.itemgetter(1))
            x = 1
            for i in name_rank:
                if i[0] == triplet[2]:
                    break
                x += 1
            self.rank.append((triplet, triplet[2], name_rank[0][0], x))
            print(x)
            cou += 1
            if cou % 10000 == 0:
                print(cou)

    def get_mean_rank(self):
        num = 0
        for r in self.rank:
            num += r[3]
        return num / len(self.rank)


def distance(h, t, r):
    h = array(h)
    t = array(t)
    r = array(r)
    s = h + r - t
    return linalg.norm(s)


def openD(dir, sp="\t"):
    # triple = (head, tail, relation)
    num = 0
    list = []
    with open(dir) as file:
        lines = file.readlines()
        for line in lines:
            triple = line.strip().split(sp)
            if len(triple) < 3:
                continue
            list.append(tuple(triple))
            num += 1
    print(num)
    return num, list


def load_data(str):
    fr = open(str)
    s_arr = [line.strip().split("\t") for line in fr.readlines()]
    dat_arr = [[float(s) for s in line[1][1:-1].split(", ")] for line in s_arr]
    name_arr = [line[0] for line in s_arr]
    return dat_arr, name_arr


if __name__ == '__main__':
    dir_train = "data/FB15k/train.txt"
    triple_num_train, triple_list_train = openD(dir_train)
    dir_test = "data/FB15k/test.txt"
    triple_num_test, triple_list_test = openD(dir_test)
    dir_entity_vector = "data/entityVector.txt"
    entity_vector_list, entity_list = load_data(dir_entity_vector)
    dir_relation_vector = "data/relationVector.txt"
    relation_vector_list, relation_list = load_data(dir_relation_vector)
    print("********** Start test... **********")

    test_head_raw = Test(entity_list, entity_vector_list, relation_list, relation_vector_list, triple_list_train,
                         triple_list_test)
    test_head_raw.get_rank()
    print(test_head_raw.get_mean_rank())
    test_head_raw.write_rank("data/test/" + "test_head_raw" + ".txt")
    test_head_raw.get_relation_rank()
    print(test_head_raw.get_mean_rank())
    test_head_raw.write_rank("data/test" + "testRelationRaw" + ".txt")

    test_tail_raw = Test(entity_list, entity_vector_list, relation_list, relation_vector_list, triple_list_train,
                         triple_list_test,
                         label="tail")
    test_tail_raw.get_rank()
    print(test_tail_raw.get_mean_rank())
    test_tail_raw.write_rank("data/test/" + "test_tail_raw" + ".txt")

    test_head_fit = Test(entity_list, entity_vector_list, relation_list, relation_vector_list, triple_list_train,
                         triple_list_test,
                         is_fit=True)
    test_head_fit.get_rank()
    print(test_head_fit.get_mean_rank())
    test_head_fit.write_rank("data/test/" + "test_head_fit" + ".txt")
    test_head_fit.get_relation_rank()
    print(test_head_fit.get_mean_rank())
    test_head_fit.write_rank("data/test/" + "testRelationFit" + ".txt")

    test_tail_fit = Test(entity_list, entity_vector_list, relation_list, relation_vector_list, triple_list_train,
                         triple_list_test,
                         is_fit=True, label="tail")
    test_tail_fit.get_rank()
    print(test_tail_fit.get_mean_rank())
    test_tail_fit.write_rank("data/test/" + "test_tail_fit" + ".txt")