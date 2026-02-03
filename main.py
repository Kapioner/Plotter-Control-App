from multiprocessing import Process
from multiprocessing.managers import SharedMemoryManager
from communication import process_a1
from gui import loop_b
from kinematics import calculateKinematics

if __name__ == '__main__':
    broker = "localhost"
    port = 1883
    topic = "testTopic"
    topic1 = 'pozycje'
    client_id_a = "client_a_unique"
    client_id_b = "client_b_unique"
    mem_name = "shared_memory_name"
    mem1 = SharedMemoryManager()
    mem1.start()
    mem2 = SharedMemoryManager()
    mem2.start()
    s1 = mem1.ShareableList([None,None,None,None,None,None,None,None,None,"Start", "","",""])
    s2 = mem2.ShareableList(["",None,0,0,0,None,None,None,None,"","",None,None,None,None,1,None,None,None,0,"Opusc","Opusc","1","disabled","normal","normal",None,"","AUTO",0,0,"","","",""])
    calculateKinematics(75,100,s2.shm.name,'AUTO')
# Deklaracja procesów i odpowiadających im funkcji( w target= podajemy funkcje, a w args= parametry do jej wywołania ( w tym przypadku nazwę pamięci))
    process_a = Process(target=process_a1, args=(broker, port, topic, client_id_a,s1,s2.shm.name,))
    process_b = Process(target=loop_b, args=((s1,s2.shm.name,)))
# Odpalenie procesów
    process_a.start()
    process_b.start()
# Połączenie procesów
    process_a.join()
    process_b.join()
# Zamknięcie pamięci
    s1.shm.close()
    s1.shm.unlink()