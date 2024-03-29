"""将教务处的表格处理为可供后端调用的 json 文件"""
from __future__ import annotations

import argparse
import json
import re
import xlrd

from typing import List, Set, Dict, Tuple
from collections import defaultdict


class Classroom(object):
    def __init__(self, sheet: xlrd.sheet.Sheet, start_row: int):
        subtitle = sheet.row_values(start_row + 1)[1].split()
        self.name = subtitle[1][3:]
        self.function = subtitle[2][6:]
        self.building = subtitle[3][6:]
        self.seats = int(subtitle[4][4:])
        self.schedule = self.generate_schedule(sheet, start_row)

    @staticmethod
    def generate_schedule(sheet: xlrd.sheet.Sheet, start_row: int) -> List[List[Set[int]]]:
        schedule = []
        for i in range(14):
            schedule.append([])
            current_row_value = sheet.row_values(start_row + 3 + i)
            for j in range(7):
                schedule[-1].append(Classroom.parse_single_cell(current_row_value[j + 1]))
        return schedule

    @staticmethod
    def parse_single_cell(cell: str) -> Set[int]:
        cell_data = set()
        busy_weeks = list(map(lambda x: x.strip(), re.findall(r'(.*)周\[\d*节]', cell)))
        for week_section in busy_weeks:
            weeks_list = week_section.split(',')
            for weeks in weeks_list:
                # 在本部的课表中，单双周基本上为 '1单周' 这种格式，我们将其视为课表的错误
                if weeks.endswith('单') or weeks.endswith('双'):
                    weeks = weeks[:-1]
                week_range = weeks.split('-')
                if len(week_range) == 2:
                    for i in range(int(week_range[0]), int(week_range[1]) + 1):
                        cell_data.add(i)
                if len(week_range) == 1:
                    cell_data.add(int(week_range[0]))
        return cell_data

    def merge_schedule(self, other: Classroom):
        for i in range(14):
            for j in range(7):
                self.schedule[i][j] = self.schedule[i][j].union(other.schedule[i][j])

    def merge_tuple(self, other: Tuple[int, Tuple[int, int], Tuple[Tuple[int, int], int], str]):
        weeks = set()
        filtered = other[2][1]
        for i in range(other[2][0][0], other[2][0][1] + 1):
            if filtered == 0 or (filtered == 1 and i % 2 == 1) or (filtered == 2 and i % 2 == 0):
                weeks.add(i)
        for i in range(other[1][0], other[1][1] + 1):
            self.schedule[i - 1][other[0]] = self.schedule[i - 1][other[0]].union(weeks)

    def is_free(self, week: int, day: int, time: int) -> bool:
        return week not in self.schedule[time][day]

    def to_dict(self) -> Dict:
        dict_result = {
            'name': self.name,
            'function': self.function,
            'building': self.building,
            'seats': self.seats,
            'schedule': []
        }
        for i in range(14):
            dict_result['schedule'].append([])
            for j in range(7):
                dict_result['schedule'][-1].append(list(self.schedule[i][j]))
        return dict_result

    def to_info_dict(self) -> Dict:
        return {
            'name': self.name,
            'function': self.function,
            'seats': self.seats,
        }


class Sheet(object):
    def __init__(self, file_name: str, sheet_name='Sheet1'):
        workbook = xlrd.open_workbook(file_name)
        self.sheet = workbook.sheet_by_index(0)
        self.iterator = -1

    def reset_iterator(self):
        self.iterator = -1

    def valid_row_index(self, row_index: int) -> bool:
        return row_index < self.sheet.nrows

    def find_next_classroom(self):
        self.iterator += 1
        while self.valid_row_index(self.iterator) \
                and not self.sheet.row_values(self.iterator)[0].startswith('北京邮电大学'):
            self.iterator += 1
        return self.valid_row_index(self.iterator)

    def generate_single_classroom_info(self) -> Classroom:
        return Classroom(self.sheet, self.iterator)

    def generate_classrooms_info(self) -> List[Classroom]:
        classroom_list = []
        while self.find_next_classroom():
            classroom_list.append(self.generate_single_classroom_info())
        self.reset_iterator()
        return classroom_list

    def generate_classrooms_info_dict(self):
        classroom_dict = {}
        while self.find_next_classroom():
            info = self.generate_single_classroom_info()
            classroom_dict[info.name] = info
        self.reset_iterator()
        return classroom_dict


def generate_graduate_schedule_list(graduate_sheet: List[str]) \
        -> List[Tuple[int, Tuple[int, int], Tuple[Tuple[int, int], int], str]]:
    schedule_list = []
    for file in graduate_sheet:
        workbook = xlrd.open_workbook(file)
        sheet = workbook.sheet_by_index(0)
        for i in range(1, sheet.nrows):
            temp = get_single_graduate_tuple(sheet.row_values(i)[7])
            if temp:
                schedule_list.append(temp)
    return schedule_list


def get_single_graduate_tuple(value) -> Tuple[int, Tuple[int, int], Tuple[Tuple[int, int], int], str] | None:
    if value.strip().startswith('参见') or value.strip().startswith('查看'):
        return None
    real_data = re.findall(r'^([^;]*)\((\d*-\d*)节\)\[(.*)]', value)
    if len(real_data) != 1 or len(real_data[0]) != 3:
        return None
    real_data = real_data[0]
    info = real_data[2].split(',')
    day = day_to_int(real_data[0])
    graduate_cell = (day, time_to_tuple(real_data[1]),
                     week_to_tuple(info[0]), location_to_classroom(info[-1]))
    if day == -1:
        return None
    return graduate_cell


def day_to_int(day: str) -> int:
    if len(day) == 0:
        return -1
    s = '一二三四五六七'
    t = day[-1]
    for index, value in enumerate(s):
        if t == value:
            return index
    return -1


def time_to_tuple(time: str) -> Tuple[int, int]:
    temp = list(map(int, time.split('-')))
    return temp[0], temp[1]


def week_to_tuple(week: str) -> Tuple[Tuple[int, int], int]:
    week_filter = 0
    week = week[:-1]
    if week.endswith('单'):
        week_filter = 1
        week = week[:-1]
    if week.endswith('双'):
        week_filter = 2
        week = week[:-1]
    for week_range in week.split('、'):
        week_range_list = list(map(int, week_range.split('-')))
        if len(week_range_list) == 1:
            return (week_range_list[0], week_range_list[0]), week_filter
        return (week_range_list[0], week_range_list[1]), week_filter


def location_to_classroom(location: str) -> str:
    return location[3:].replace('经-', '经管楼-')


def get_classrooms(sheet_by_room: List[str], graduate_sheet: List[str]) -> List[Classroom]:
    if len(sheet_by_room) < 1:
        return []
    if len(sheet_by_room) == 1:
        return Sheet(sheet_by_room[0]).generate_classrooms_info()
    all_classrooms = Sheet(sheet_by_room[0]).generate_classrooms_info_dict()
    cdr = sheet_by_room[1:]
    for sheet in cdr:
        classrooms = Sheet(sheet).generate_classrooms_info()
        for classroom in classrooms:
            if classroom.name in all_classrooms:
                all_classrooms[classroom.name].merge_schedule(classroom)
            else:
                all_classrooms[classroom.name] = classroom
    for t in generate_graduate_schedule_list(graduate_sheet):
        if t[-1] in all_classrooms:
            all_classrooms[t[-1]].merge_tuple(t)

    return list(all_classrooms.values())


def filter_classrooms(classrooms: List[Classroom],
                      function_allow_list=None,
                      name_deny_list=None) -> List[Classroom]:
    if function_allow_list is None:
        function_allow_list = []
    if name_deny_list is None:
        name_deny_list = []

    filtered_classrooms = list(filter(lambda x: not x.seats == 0, classrooms))
    for prefix in function_allow_list:
        filtered_classrooms = list(filter(lambda x: x.function.startswith(prefix), filtered_classrooms))
    for prefix in name_deny_list:
        filtered_classrooms = list(filter(lambda x: not x.name.startswith(prefix), filtered_classrooms))
    return filtered_classrooms


def get_classroom_dict(classrooms: List[Classroom]) -> Dict[str, List[Classroom]]:
    classroom_dict = defaultdict(list)
    for i in classrooms:
        classroom_dict[i.building].append(i)
    return classroom_dict


def get_free_classroom_dict(classroom_dict: Dict[str, List[Classroom]]):
    free_classroom_dict = {}
    for week in range(1, 19):
        for day in range(7):
            for time in range(14):
                week_str = '%02d' % week
                day_str = '%d' % day
                time_str = '%02d' % time
                key = week_str + '.' + day_str + '.' + time_str
                value = {}
                for i in classroom_dict.keys():
                    temp = []
                    for j in classroom_dict[i]:
                        if j.is_free(week, day, time):
                            temp.append(j.to_info_dict())
                        temp.sort(key=lambda x: x['name'])
                    if len(temp) > 0:
                        value[i] = temp
                value_list = []
                for k, v in value.items():
                    value_list.append({'building': k, 'classrooms': v})
                value_list.sort(key=lambda x: x['classrooms'][0]['name'])
                free_classroom_dict[key] = value
    return free_classroom_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="<required> writes our JSON file to this path", required=True)
    parser.add_argument('-c', '--classroom', nargs='+', help='<required> classroom files', required=True)
    parser.add_argument('-g', '--graduate', nargs='+', help='<required> classroom files')
    args = parser.parse_args()
    graduate = [] if not args.graduate else args.graduate
    classrooms = get_classrooms(args.classroom, graduate)
    filtered = filter_classrooms(classrooms, function_allow_list=['多媒体'], name_deny_list=['教师自行安排', '网络教室', '体育', '虚拟'])
    result = get_free_classroom_dict(get_classroom_dict(filtered))
    with open(args.output, mode='w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    f.close()


if __name__ == '__main__':
    main()
