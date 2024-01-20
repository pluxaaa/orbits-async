from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests
from concurrent import futures

CALLBACK_URL = "http://127.0.0.1:8000/transfer_requests/get_success"
AUTH_KEY = "secret-async-orbits"

executor = futures.ThreadPoolExecutor(max_workers=1)

def get_random_status(id):
    time.sleep(5)
    return {
        "id": id,
        "status": bool(random.getrandbits(1)),
    }

def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return
    
    nurl = str(CALLBACK_URL + "/" + str(result["id"]))
    answer = {"id": result["id"], "status": result["status"]}

    headers = {
        'Authorization': AUTH_KEY
    }
    
    requests.post(nurl, json=answer, headers=headers, timeout=3)

@api_view(['POST'])
def set_status(request):
    if "id" in request.data.keys():   
        id = request.data["id"]        

        task = executor.submit(get_random_status, id)
        task.add_done_callback(status_callback)
        return Response(status=status.HTTP_200_OK)
    
    return Response(status=status.HTTP_400_BAD_REQUEST)
