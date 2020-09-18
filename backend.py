"""后端程序，使用 SLEEP_LIST=<parse_xls 生成的 json 文件位置> uvicorn backend:app --host 0.0.0.0 --port 4514 启动"""
import copy
import json
import os

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from starlette.exceptions import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from typing import List, Tuple, Dict

decoded_data = {}


def to_tuple(data: Dict) -> Tuple[str, str, str]:
    return data['name'], data['function'], data['seats']


def load_data():
    global decoded_data
    if 'SLEEP_LIST' not in os.environ:
        raise Exception('SLEEP_LIST is not defined.')
    with open(os.environ['SLEEP_LIST'], mode='r', encoding='utf-8') as f:
        data = json.load(f)
    for k, v in data.items():
        temp = {}
        for k_2, v_2 in v.items():
            temp[k_2] = list(map(to_tuple, v_2))
        decoded_data[k] = temp


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://where-to-sleep.name1e5s.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", load_data)


def check_time(time) -> bool:
    if not time:
        return False
    for i in time:
        if i < 1 or i > 14:
            return False
    return True


@app.get("/free_classrooms")
async def read_item(week: int = 3, day: int = 1, time: List[int] = Query(None)):
    if week > 18 or week < 1 or day > 7 or day < 1 or not check_time(time):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Week {week}; day {day}; time {time} not found"
        )
    data = merge_data(get_data(week, day, time))
    return dict_to_list(data)


def get_data(week: int, day: int, time) -> List:
    week_str = '%02d' % week
    day_str = '%d' % (day - 1)
    result = []
    for i in time:
        time_str = '%02d' % (i - 1)
        key = week_str + '.' + day_str + '.' + time_str
        result.append(decoded_data[key])
    return result


def merge_data(data):
    if len(data) == 0:
        return {}
    if len(data) == 1:
        return data[0]
    result = copy.deepcopy(data[0])
    for i in range(1, len(data)):
        for j in result.keys():
            if j not in data[i].keys():
                result[j] = []
        for k, v in data[i].items():
            if k not in result.keys():
                result[k] = []
            else:
                temp = list(set(result[k]) & set(v))
                result[k] = temp
    return result


def dict_to_list(data):
    result = []
    for k, v in data.items():
        if len(v) > 0:
            v.sort(key=lambda x: x[0])
            result.append({"building": k, "classrooms": list(map(lambda x: {
                'name': x[0],
                'function': x[1],
                'seats': x[2]}, v))})
    result.sort(key=lambda x: x['classrooms'][0]['name'])
    return result
