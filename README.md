�ù��̴�����Ҫ��ʵ���Լ��Ķ����ĺ�֪ʶͼ����صľ����㷨�Ĵ��룺
1.TransE��֪ʶͼ����֪ʶ��ʾ�ľ����㷨������ʵ����ѵ�����루�����ͨ�Ű棩�Ͳ��Դ���
������������������Ķ��Ჹ����Ӧ�Ĵ���
2.����data�ļ������޷��ϴ�������https://github.com/thunlp/KB2E����data.zip����ѹ�����̵�data·��
3.TransE���ĵ�ַ�� https://www.utc.fr/~bordesan/dokuwiki/_media/en/transe_nips13.pdf
###ѵ������
####Simple�汾
./train_fb15k.sh 0
����ʹ��Python��ɶ�Ӧ��ѵ������
####Manager�汾
./train_fb15k.sh 1
��TransE���ʵ���ڶ����֮�䴫��
####Queue�汾
./train_fb15k.sh 2
��TransE���ѵ�����ݴ�����У���С���̿������ӿ�ѵ���ٶ�

��ѵ�����֮���ٽ��в���
###���Բ���
####TestTransEMqQueue
python TestTransEMpQueue.py
����̶��в��Լ��٣�Ч�������ԣ�����������0.5s�����Խ�����Ҫ��5h��
####TestMainTF
 python TestMainTF.py
tf�����̲��Լ��٣�Ч�����������Խ�������Ҫ8min���ҡ�
###���ղ��Խ��
 	            FB15k
epochs:2000		MeanRank		Hits@10
			raw	     filter		raw	   filter
head		320.743	 192.152	29.7	41.2
tail		236.984	 153.431	36.1	46.2
average		278.863	 172.792	32.9	43.7
paper		243	     125	    34.9	47.1