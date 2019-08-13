from multiprocessing import Process, Lock
from multiprocessing.managers import BaseManager
import logging
from TrainTransESimple import TransE as TransESimple
from TrainTransESimple import prepare_fb15k_train_data

LOG_FORMAT = "%(asctime)s - %(name)s - %(message)s"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

INITIAL_LEARNING_RATE = 0.01


class TransE(TransESimple):

    def get_loss(self):
        # �ο��廪��Fast-TransX��C++���룬ȷʵ�ٶȺܿ죬Python�ӽ�10��Сʱ��ѵ��C++�����ʮ�����Ӽ�����ɡ����ԵĿ���һ�´��룬
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

    def transE(self):
        Sbatch = self.sample(self.batch_size // 10)
        Tbatch = []  # Ԫ��ԣ�ԭ��Ԫ�飬�������Ԫ�飩���б� ��{((h,r,t),(h',r,t'))}
        for sbatch in Sbatch:
            pos_neg_triplets = (sbatch, self.get_corrupted_triplets(sbatch))
            if pos_neg_triplets not in Tbatch:
                Tbatch.append(pos_neg_triplets)
        self.update(Tbatch)


class MyManager(BaseManager):
    pass


def Manager2():
    m = MyManager()
    m.start()
    return m


MyManager.register('TransE', TransE)


def func1(em, lock):
    with lock:
        em.transE()


def main():
    manager = Manager2()
    entity_list, rels_list, train_triplets_list = prepare_fb15k_train_data()

    transE = manager.TransE(
        entity_list,
        rels_list,
        train_triplets_list,
        batch_size=10000,
        margin=1,
        dim=50)
    logging.info("TransE is initializing...")
    for i in range(20000):  # epoch�Ĵ���
        lock = Lock()
        proces = [Process(target=func1, args=(transE, lock))
                  for j in range(10)]  # 10������̣��������У����Ի�ܿ�
        for p in proces:
            p.start()
        for p in proces:
            p.join()
        if i != 0:
            logging.info(
                "After %d training epoch(s), loss on batch data is %g" %
                (i * 10, transE.get_loss()))
        transE.clear_loss()
    # transE.transE(100000)
    logging.info("********** End TransE training ***********\n")


if __name__ == "__main__":
    main()