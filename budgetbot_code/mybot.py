



# from squad.demo_prepro import prepro
# from basic.demo_cli import Demo
# import json
import data
# import random
# import string


# import multiprocessing

# from multiprocessing import Pool
index, budget_data, tfidf_table = data.index_and_data()
# question = "who is giving speech"
# def f(item):
#   demo = Demo()
#   paragraph = item['body']
#   # print("total " +str(count) +" start");import time;start = time.time()
#   question = "Who is minister"
#   pq_prepro = prepro(paragraph, question)
#   res = demo.run(pq_prepro)
#   # print("res::")
#   # print(paragraph)
#   return res

# pool = multiprocessing.Pool(5)
# results = pool.map(f, budget_data[:10])
# pool.close()
# pool.join()
# with Pool(5) as p:
# mama = p.map(f, budget_data[:10])
# p1 = multiprocessing.Process(target=f,args=(budget_data[2],))
# p2 = multiprocessing.Process(target=f,args=(budget_data[22],))
# p3 = multiprocessing.Process(target=f,args=(budget_data[24],))
# p1.start()
# p2.start()
# p3.start()
# p1.join()
# p2.join()
# p3.join()

# if __name__ == '__main__':
#     multiprocessing.set_start_method('spawn') 
#     multiprocessing.Pool().map(f, budget_data[:10])
import os
import random
import json
import re

def process_x(item):
    #================  Get title ==================#
    paragraph = item['body']
    question = item['question']
    # print("total " +str(count) +" start");import time;start = time.time()
    # print("res::")
    port = random.randint(2000,2020)
    # http://ec2-107-22-58-162.compute-1.amazonaws.com/
    # cmd = "curl -G 'http://ec2-107-22-58-162.compute-1.amazonaws.com:"+str(port)+"/submit' --data-urlencode 'question="+question+"'  --data-urlencode \"paragraph="+paragraph.replace("\"", "'")+"\""
    cmd = "curl -G 'localhost:"+str(port)+"/submit' --data-urlencode 'question="+question+"'  --data-urlencode \"paragraph="+paragraph.replace("\"", "'")+"\""
    # print(cmd)
    res = os.popen(cmd).read()
    # print("res")
    # print(res)
    try:

        res = json.loads(res)
    
    except Exception as e:
        res = {'result': "", 'scores': 0}
    res['url'] = item['url']
    res['idx'] = item['idx']
    res['snippet'] = re.findall(r"([^.]*?"+res['result']+"[^.]*\.)",budget_data[item['idx']]['body'])[0]
    return res 


# pool = Pool(processes=4)             # start 4 worker processes
# question = "Who is prime minister"
def get_answers(question):
    to_send = []
    question = question.lower()
    stop_words = ['the','of','to','and','in','a','for','is','on','that','be','will','tax','The','as','has','are','from','by','with','have', 'who', 'what', 'how', 'there', 'when', 'where', 'which', 'why', 'budget']
    imp_words = [item for item in question.split() if item not in stop_words]
    query = " OR ".join(imp_words)
    # print(query)
    # relevant_documents = index.query(query)
    # print(relevant_documents[0])
    relevant_documents_tfidf = tfidf_table.similarities(imp_words)[-10:]
    # relevant_documents_tfidf = sorted(relevant_documents_tfidf, key=lambda k: k[1])[:30]
    
    for i in relevant_documents_tfidf:
        item = budget_data[i[0]]
        item['question'] = question
        item['idx'] = i[0]
        to_send = to_send + [item]
    # result_list = pool.map(process_x, to_send)
    result_list = []
    for to_send_item in to_send:
        result_list = result_list + [process_x(to_send_item)]
    result_list = sorted(result_list, key=lambda k: k['scores'])
    return result_list





# from squad.demo_prepro import prepro
# from basic.demo_cli import Demo
# import json
# import data
# index, budget_data, tfidf = data.index_and_data()
# demo = Demo()
# import random


# def get_answers(question, budget_data_count):
#   result = []
#   count = 0
#   for item in budget_data[:budget_data_count]:
#     count = count + 1
#     if count%10 == 0:
#       print("completed:") 
#       print(count) 
#     paragraph = item['body']
#     # print("total " +str(count) +" start");import time;start = time.time()
#     pq_prepro = prepro(paragraph, question)
#     res = demo.run(pq_prepro)
#     # print("total stop:" + str(time.time() - start))
#     result = result + [{'raw':res, 'res': res.id2answer_dict}]
#   sorted(result, key=lambda k: k['res']['scores'][0])
#   return result
# # print("total start");import time;start = time.time()
# # pq_prepro = prepro(budget_data[45]['body'], "Who is minister")
# # res = demo.run(pq_prepro)



# # print("total stop:" + str(time.time() - start))
