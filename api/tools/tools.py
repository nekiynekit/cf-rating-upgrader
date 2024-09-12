import datetime
import random as rd
import time

import requests as rq


class Problem:
    def __init__(self, source_json_dict):
        self.source = source_json_dict
        try:
            self.rating = int(self.source["rating"])
            self.contest = self.source["contestId"]
            self.index = self.source["index"]
            self.address = f"https://codeforces.com/contest/{self.contest}/problem/{self.index}"
            self.broken = False
        except KeyError:
            self.broken = True

    def __str__(self) -> str:
        if self.broken:
            return ""
        return self.address

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Problem):
            return False
        verdict = not self.broken
        verdict &= not value.broken
        verdict &= self.rating == value.rating
        verdict &= self.address == value.address
        return verdict

    def valid_rating(self, rating):
        return not self.broken and rating == self.rating


class Submission:
    def __init__(self, source_json_dict):
        self.source = source_json_dict
        try:
            self.verdict = self.source["verdict"]
            self.problem = Problem(self.source["problem"])
            self.broken = False
            if self.problem.broken:
                self.broken = True
        except KeyError:
            self.broken = True

    def solved_and_rating_is(self, rating):
        return not self.broken and self.problem.valid_rating(rating) and self.verdict


def problems_solved_by(handle="rmnv", rating=1900):
    submissions = rq.get(f"https://codeforces.com/api/user.status?handle={handle}").json()["result"]
    submissions = list(map(Submission, submissions))
    submissions = list(filter(lambda sub: sub.solved_and_rating_is(rating), submissions))
    problems = list(map(lambda x: x.problem, submissions))
    return problems


def select_task_by_rating(rating=1900, shuffle=True, handle="rmnv"):

    if shuffle:
        date = datetime.date.today()
        day, month, year = date.day, date.month, date.year
        seed = day + month * 31 + year * 365
        rd.seed(seed)

    problems = rq.get("https://codeforces.com/api/problemset.problems").json()["result"]["problems"]
    problems = list(map(Problem, problems))
    problems = list(filter(lambda task: task.valid_rating(rating), problems))

    if handle:
        solved = problems_solved_by(handle, rating)

        def already_solved(problem: Problem) -> bool:
            for solved_task in solved:
                if solved_task == problem:
                    return False
            return True

        problems = list(filter(already_solved, problems))

    if shuffle:
        rd.shuffle(problems)

    return problems


def get_best_rating(handle, increment=200):
    ratings = rq.get(f"https://codeforces.com/api/user.rating?handle={handle}").json()["result"]
    cur_rating = ratings[-1]["newRating"]
    cur_rating = int(cur_rating)
    best_rating = cur_rating + increment
    if best_rating % 100 > 49:
        best_rating += 100
    best_rating = (best_rating // 100) * 100
    return best_rating