#!/usr/bin/python3
"""
picoCTF Profiling script
"""
from pyinstrument import Profiler
from line_profiler import LineProfiler
from argparse import ArgumentParser 
import api
import random
operations = []

def profile(func, *args, **kwargs):
    operations.append((func, args, kwargs))

    func(*args, **kwargs)

def register_users(users):
    users = [
        {
            "username": "user" + str(i),
            "password": "valid",
            "email": "valid@hs.edu",
            "create-new-team": "on",

            "team-name-new": "team" + str(i),
            "team-adv-name-new": "Dr. Hacks",
            "team-adv-email-new": "hacks@hs.edu",
            "team-school-new": "Hacks HS",
            "team-password-new": "leet_hax"
        }
        for i in range(users)
    ]

    for user in users:
        api.user.create_user_request(user)

def submit_problems():
    picked = random.sample(api.user.get_all_users(), 5)

    uids = [user['uid'] for user in picked]
    tids = [api.user.get_team(uid=uid)['tid'] for uid in uids]

    for uid, tid in zip(uids, tids):
        unlocked = set(api.problem.get_unlocked_pids(tid))
        done = set(api.problem.get_solved_pids(tid=tid))

        new = unlocked - done

        chosen = random.sample(new, 3) if len(new) > 3 else new

        for pid in chosen:
            if random.random() < 0.9:
                key = "test" #correct
            else:
                key = str(random.randint(0, 50))

            profile(api.problem.submit_key, tid, pid, "test", uid=uid)

def get_scoreboard():
    profile(api.scoreboard.get_all_team_scores)

def simulate_competition(calls):
    ops = [submit_problems, get_scoreboard]
    for i in range(calls):
        random.choice(ops)()

def run_profiling(args):
    lprofiler = LineProfiler() 

    monitor_fuctions = [api.problem.submit_key, api.problem.get_unlocked_pids, api.problem.get_solved_pids,
                        api.problem.get_all_problems, api.problem.get_solved_problems, api.scoreboard.get_score,
			api.cache.memoize]

    for func in monitor_fuctions:
        lprofiler.add_function(func)

    lprofiler.enable()

    if args.stack:
        profiler = Profiler(use_signal=False)
        profiler.start()

    for func, a, kw in operations:
        func(*a, **kw)

    if args.stack:
        profiler.stop()

    lprofiler.disable()

    if args.print:
        print(profiler.output_text(unicode=True, color=True))
        lprofiler.print_stats()

    output = open(args.output, "w")

    if args.stack:
        output.write(profiler.output_text(unicode=True))

        if args.output_html is not None:
            output_html = open(args.output_html, "w")
            output_html.write(profiler.output_html())
            output_html.close()
            print("Wrote test info to " + args.output_html)

    lprofiler.print_stats(output)
    output.close()
    print("Wrote test info to " + args.output)


def main():

    parser = ArgumentParser(description="picoCTP API performace profiling")
    parser.add_argument("-p", "--print", action="store_true", help="print output to console", default=False)
    parser.add_argument("-o", "--output", required=True, action="store", help="file to store statistics")
    parser.add_argument("-w", "--output-html", action="store", help="file to store html statistics", default=None)
    parser.add_argument("-u", "--users", action="store", type=int, help="number of users to insert", default=2000)
    parser.add_argument("-c", "--calls", action="store", type=int, help="number of API calls to make", default=10000)
    parser.add_argument("-s", "--stack-profile", dest="stack", action="store_true", help="run the stack trace profiler", default=False)

    args = parser.parse_args()

    # setup the db for testing
    db = api.common.get_conn()
    db.users.remove()
    db.teams.remove()
    db.submissions.remove()

    print("Registering users...")

    register_users(args.users)

    print("Running simulation...")

    simulate_competition(args.calls)

    db.submissions.remove()

    api.cache.clear_all()
    print("Re-running operations with profiling...")

    run_profiling(args)

main()
