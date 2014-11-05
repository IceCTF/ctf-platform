""" Module for getting competition statistics"""

import api
import datetime
import pymongo
import statistics
from collections import defaultdict
from hashlib import sha1

_get_problem_names = lambda problems: [problem['name'] for problem in problems]
top_teams = 10

@api.cache.memoize()
def get_score(tid=None, uid=None):
    """
    Get the score for a user or team.

    Args:
        tid: The team id
        uid: The user id
    Returns:
        The users's or team's score
    """
    score = sum([problem['score'] for problem in api.problem.get_solved_problems(tid=tid, uid=uid)])
    return score


def get_team_review_count(tid=None, uid=None):
    if uid is not None:
        return len(api.problem_feedback.get_reviewed_pids(uid=uid))
    elif tid is not None:
        count = 0
        for member in api.team.get_team_members(tid=tid):
            count += len(api.problem_feedback.get_reviewed_pids(uid=member['uid']))
        return count


def get_group_scores(gid=None, name=None):
    """
    Get the group scores.

    Args:
        gid: The group id
        name: The group name
    Returns:
        A dictionary of tid:score mappings
    """

    members = [api.team.get_team(tid=tid) for tid in api.group.get_group(gid, name)['members']]

    result = []
    for team in members:
        result.append({
            "name": team['team_name'],
            "score": get_score(tid=team['tid'])
        })

    return sorted(result, key=lambda entry: entry['score'], reverse=True)

def get_group_average_score(gid=None, name=None):
    """
    Get the average score of teams in a group.

    Args:
        gid: The group id
        name: The group name
    Returns:
        The total score of the group
    """

    group_scores = get_group_scores(gid=gid, name=name)
    total_score = sum([entry['score'] for entry in group_scores])
    return int(total_score / len(group_scores)) if len(group_scores) > 0 else 0

# Stored by the cache_stats daemon
@api.cache.memoize()
def get_all_team_scores():
    """
    Gets the score for every team in the database.

    Returns:
        A list of dictionaries with name and score
    """

    teams = api.team.get_all_teams()
    db = api.api.common.get_conn()

    result = []
    for team in teams:
        team_query = db.submissions.find({'tid': team['tid'], 'eligible': True, 'correct': True})
        if team_query.count() > 0:
            lastsubmit = team_query.sort('timestamp', direction=pymongo.DESCENDING)[0]['timestamp']
        else:
            lastsubmit = datetime.datetime.now()
        score = get_score(tid=team['tid'])
        if score > 0:
            result.append({
                "name": team['team_name'],
                "tid": team['tid'],
                "school": team["school"],
                "score": score,
                "lastsubmit": lastsubmit
            })

    time_ordered = sorted(result, key=lambda entry: entry['lastsubmit'])    
    time_ordered_time_removed = [{'name': x['name'], 'tid': x['tid'], 'school': x['school'], 'score': x['score']} for x in time_ordered]
    return sorted(time_ordered_time_removed, key=lambda entry: entry['score'], reverse=True)


def get_all_user_scores():
    """
    Gets the score for every user in the database.

    Returns:
        A list of dictionaries with name and score
    """

    users = api.user.get_all_users()

    result = []
    for user in users:
        result.append({
            "name": user['username'],
            "score": get_score(uid=user['uid'])
        })

    return sorted(result, key=lambda entry: entry['score'], reverse=True)

@api.cache.memoize(timeout=120, fast=True)
def get_problems_by_category():
    """
    Gets the list of all problems divided into categories

    Returns:
        A dictionary of category:[problem list]
    """

    result = {cat: _get_problem_names(api.problem.get_all_problems(category=cat))
                            for cat in api.problem.get_all_categories()}

    return result


@api.cache.memoize(timeout=120, fast=True)
def get_pids_by_category():
    result = {cat: [x['pid'] for x in api.problem.get_all_problems(category=cat)]
              for cat in api.problem.get_all_categories()}
    return result


@api.cache.memoize(timeout=120, fast=True)
def get_pid_categories():
    pid_map = {}
    for cat in api.problem.get_all_categories():
        for p in api.problem.get_all_problems(category=cat):
            pid_map[p['pid']] = cat
    return pid_map


def get_team_member_stats(tid):
    """
    Gets the solved problems for each member of a given team.

    Args:
        tid: the team id

    Returns:
        A dict of username:[problem list]
    """

    members = api.team.get_team_members(tid=tid)

    return {member['username']: _get_problem_names(api.problem.get_solved_problems(uid=member['uid'])) for member in members}

@api.cache.memoize()
def get_score_progression(tid=None, uid=None, category=None):
    """
    Finds the score and time after each correct submission of a team or user.
    NOTE: this is slower than get_score. Do not use this for getting current score.

    Args:
        tid: the tid of the user
        uid: the uid of the user
        category: category filter
    Returns:
        A list of dictionaries containing score and time
    """

    correct_submissions = api.problem.get_submissions(uid=uid, tid=tid, category=category, correctness=True)

    result = []
    score = 0

    for submission in sorted(correct_submissions, key=lambda sub: sub["timestamp"]):
        score += api.problem.get_problem(pid=submission["pid"])["score"]
        result.append({
            "score": score,
            "time": int(submission["timestamp"].timestamp())
        })

    return result

def get_top_teams():
    """
    Finds the top teams

    Returns:
        The top teams and their scores
    """

    all_teams = api.stats.get_all_team_scores()
    return all_teams if len(all_teams) < top_teams else all_teams[:top_teams]

# Stored by the cache_stats daemon
@api.cache.memoize()
def get_top_teams_score_progressions():
    """
    Gets the score_progressions for the top teams

    Returns:
        The top teams and their score progressions.
        A dict of {team_name: score_progression}
    """

    return [{
        "name": team["name"],
        "score_progression": get_score_progression(tid=team["tid"]),
    } for team in get_top_teams()]


# Custom statistics not necessarily to be served publicly

def bar():
    print("------------------")


def get_stats():
    bar()
    print("Average Eligible, Scoring Team Score: {0:.3f} +/- {1:.3f}".format(*get_average_eligible_score()))
    print("Median Eligible, Scoring Team Score: {0:.3f}".format(get_median_eligible_score()))
    bar()
    print("Average Number of Problems Solved per Team (eligible, scoring): {0:.3f} +/- {1:.3f}".format(*get_average_problems_solved()))
    print("Median Number of Problems Solved per Team (eligible, scoring): {:.3f}".format(get_median_problems_solved()))
    bar()
    user_breakdown = get_team_member_solve_stats()
    print("Average Number of Problems Solved per User (eligible, user scoring): {0:.3f} +/- {1:.3f}".format(*get_average_problems_solved_per_user(user_breakdown=user_breakdown)))
    print("Median Number of Problems Solved per User (eligible, user scoring): {:.3f}".format(get_median_problems_solved_per_user(user_breakdown=user_breakdown)))
    bar()
    print("Team participation averages:")
    correct_percent, any_percent = get_team_participation_percentage(user_breakdown=user_breakdown)
    for size in sorted(correct_percent.keys()):
        print("\tTeam size: {0}\t{1:.3f} submitted a correct answer\t{2:.3f} submitted some answer".
              format(size, correct_percent[size], any_percent[size]))

    bar()
    print("User background breakdown:")
    for background, count in sorted(get_user_backgrounds().items(), key=lambda x: x[1], reverse=True):
        print("{0:30} {1}".format(background, count))
    bar()
    print("User country breakdown:")
    for country, count in sorted(get_user_countries().items(), key=lambda x: x[1], reverse=True)[0:15]:
        print("%s: %s" % (country, count))
    print("...")
    bar()
    print("Event ID breakdown:")
    for eventid, count in sorted(get_user_game_progress().items(), key=lambda x: x[0]):
        print("{0:60} {1}".format(eventid, count))
    bar()
    print("Average Achievement Number:")
    print("Average Number of Achievements per Team (all teams): %s +/- %s" % get_average_achievement_number())
    print("Achievement breakdown:")
    for achievement, count in sorted(get_achievement_frequency().items(), key=lambda x: x[1], reverse=True):
        print("{0:30} {1}".format(achievement, count))
    bar()
    print("Average # per category per eligible team")
    for cat, count in get_category_solves().items():
        print("{0:30} {1:.3f}".format(cat, count))
    bar()
    print("Number of days worked by teams")
    for number, count in get_days_active_breakdown(user_breakdown=user_breakdown).items():
        print("%s Days: %s Teams" % (number, count))
    bar()
    print("REVIEWS:")
    bar()
    review_data = get_review_stats()
    print("Problems by Reviewed Educational Value (10+ Reviews)")
    for problem in sorted(review_data, key=lambda x: x['education']):
        if problem['votes'] > 10:
            print("{name:30} {education:.3f} ({votes} reviews)".format(**problem))
    bar()
    print("Problems by Reviewed Enjoyment (10+ Reviews)")
    for problem in sorted(review_data, key=lambda x: x['enjoyment']):
        if problem['votes'] > 10:
            print("{name:30} {enjoyment:.3f} ({votes} reviews)".format(**problem))
    bar()
    print("Problems by Reviewed Difficulty (10+ Reviews)")
    for problem in sorted(review_data, key=lambda x: x['difficulty']):
        if problem['votes'] > 10:
            print("{name:30} {difficulty:.3f} ({votes} reviews)".format(**problem))
    bar()


def get_average_eligible_score():
    return (statistics.mean([x['score'] for x in get_all_team_scores()]),
            statistics.stdev([x['score'] for x in get_all_team_scores()]))


def get_median_eligible_score():
    return statistics.median([x['score'] for x in get_all_team_scores()])


def get_average_problems_solved(eligible=True, scoring=True):
    teams = api.team.get_all_teams(show_ineligible=(not eligible))
    values = [len(api.problem.get_solved_pids(tid=t['tid'])) for t in teams
              if not scoring or len(api.problem.get_solved_pids(tid=t['tid'])) > 0]
    return statistics.mean(values), statistics.stdev(values)


def get_median_problems_solved(eligible=True, scoring=True):
    teams = api.team.get_all_teams(show_ineligible=(not eligible))
    return statistics.median([len(api.problem.get_solved_pids(tid=t['tid'])) for t in teams
                             if not scoring or len(api.problem.get_solved_pids(tid=t['tid'])) > 0])


def get_average_problems_solved_per_user(eligible=True, scoring=True, user_breakdown=None):
    if user_breakdown is None:
        user_breakdown = get_team_member_solve_stats(eligible)
    solves = []
    for tid, breakdown in user_breakdown.items():
        for uid, ubreakdown in breakdown.items():
            if ubreakdown is None:
                solved = 0
            else:
                if 'correct' in ubreakdown:
                    solved = ubreakdown['correct']
                else:
                    solved = 0
            if solved > 0 or not scoring:
                solves += [solved]
    return (statistics.mean(solves),
            statistics.stdev(solves))


def get_median_problems_solved_per_user(eligible=True, scoring=True, user_breakdown=None):
    if user_breakdown is None:
        user_breakdown = get_team_member_solve_stats(eligible)
    solves = []
    for tid, breakdown in user_breakdown.items():
        for uid, ubreakdown in breakdown.items():
            if ubreakdown is None:
                solved = 0
            else:
                if 'correct' in ubreakdown:
                    solved = ubreakdown['correct']
                else:
                    solved = 0
            if solved > 0 or not scoring:
                solves += [solved]
    return statistics.median(solves)


def get_user_backgrounds():
    db = api.api.common.get_conn()
    all_users = db.users.find()
    backgrounds = defaultdict(int)
    for user in all_users:
        if 'background' in user:
            backgrounds[user['background']] += 1
        else:
            print("No background for user %s" % user)
    return backgrounds


def get_user_countries():
    db = api.api.common.get_conn()
    all_users = db.users.find()
    countries = defaultdict(int)
    for user in all_users:
        countries[user['country']] += 1
    return countries


def get_user_game_progress():
    event_map = {}
    event_map[0] = "00 - Not Started"
    event_map[1] = "01 - Level 1: Father Gets Kidnapped"
    event_map[2] = "02 - Level 1: Player Looks for Father"
    event_map[3] = "03 - Level 1: Player Decides to Investigate Flash Drive"
    event_map[4] = "04 - Level 1: Player Accesses Flash Drive"
    event_map[5] = "05 - Level 1: Police Arrive"
    event_map[6] = "06 - Level 1: Player Leaves for Police HQ"
    event_map[7] = "07 - Level 2: Player Arrives at Police HQ"
    event_map[8] = "08 - Level 2: Player Gathers Enough Evidence"
    event_map[9] = "09 - Level 2: Player Receives Call From Daedalus"
    event_map[10] = "10 - Level 3: Player Arrives at Tower"
    event_map[11] = "11 - Level 3: Player Heads to Boss Room"
    event_map[12] = "12 - Level 3: Player Enters Boss Room"
    event_map[13] = "13 - Level 3: Player Defeats Boss"
    event_map[14] = "14 - Level 3: Player Enters Secret Rooms"
    event_map[15] = "15 - Level 4: Player Completes Game"
    db = api.api.common.get_conn()
    all_users = db.users.find()
    events = defaultdict(int)
    for user in all_users:
        events[user['eventid']] += 1
    pretty_events = {event_map[x]: y for x, y in events.items()}
    return pretty_events


def get_team_size_distribution(eligible=True):
    teams = api.team.get_all_teams(show_ineligible=(not eligible))
    size_dist = defaultdict(int)
    for t in teams:
        members = api.team.get_team_members(tid=t['tid'], show_disabled=False)
        if len(members) > api.team.max_team_users:
            print("WARNING: Team %s has too many members" % t['team_name'])
        size_dist[len(members)] += 1
    return size_dist


def get_team_member_solve_stats(eligible=True):
    db = api.api.common.get_conn()
    teams = api.team.get_all_teams(show_ineligible=(not eligible))
    user_breakdowns = {}
    for t in teams:
        uid_map = defaultdict(lambda: defaultdict(int))
        members = api.team.get_team_members(tid=t['tid'], show_disabled=False)
        subs = db.submissions.find({'tid': t['tid']})
        for sub in subs:
            uid = sub['uid']
            uid_map[uid]['submits'] += 1
            if uid_map[uid]['times'] == 0:
                uid_map[uid]['times'] = list()
            uid_map[uid]['times'].append(sub['timestamp'])
            if sub['correct']:
                uid_map[uid]['correct'] += 1
                uid_map[uid][sub['category']] += 1
            else:
                uid_map[uid]['incorrect'] += 1
        user_breakdowns[t['tid']] = uid_map
        for member in members:
            if member['uid'] not in uid_map:
                uid_map[uid] = None
    return user_breakdowns


def get_team_participation_percentage(eligible=True, user_breakdown=None):
    if user_breakdown is None:
        user_breakdown = get_team_member_solve_stats(eligible)
    team_size_any = defaultdict(list)
    team_size_correct = defaultdict(list)
    for tid, breakdown in user_breakdown.items():
        count_any = 0
        count_correct = 0
        for uid, work in breakdown.items():
            if work is not None:
                count_any += 1
                if work['correct'] > 0:
                    count_correct += 1
        team_size_any[len(breakdown.keys())].append(count_any)
        team_size_correct[len(breakdown.keys())].append(count_correct)
    return {x: statistics.mean(y) for x, y in team_size_any.items()}, \
           {x: statistics.mean(y) for x, y in team_size_correct.items()}


def get_achievement_frequency():
    earned_achievements = api.achievement.get_earned_achievement_instances()
    frequency = defaultdict(int)
    for achievement in earned_achievements:
        frequency[achievement['name']] += 1
    return frequency


def get_average_achievement_number():
    earned_achievements = api.achievement.get_earned_achievement_instances()
    frequency = defaultdict(int)
    for achievement in earned_achievements:
        frequency[achievement['uid']] += 1
    extra = len(api.team.get_all_teams(show_ineligible=False)) - len(frequency.keys())
    values = [0] * extra
    for val in frequency.values():
        values.append(val)
    return statistics.mean(values), statistics.stdev(values)


def get_category_solves(eligible=True):
    teams = api.team.get_all_teams(show_ineligible=(not eligible))
    category_breakdown = defaultdict(int)
    for team in teams:
        problems = api.problem.get_solved_problems(tid=team['tid'])
        for problem in problems:
            category_breakdown[problem['category']] += 1
    team_count = len(api.team.get_all_teams(show_ineligible=False))
    return {x: y / team_count for x, y in category_breakdown.items()}


def get_days_active_breakdown(eligible=True, user_breakdown=None):
    if user_breakdown is None:
        user_breakdown = get_team_member_solve_stats(eligible)
    day_breakdown = defaultdict(int)
    for tid, breakdown in user_breakdown.items():
        days_active = set()
        for uid, work in breakdown.items():
            if work is None:
                continue
            for time in work['times']:
                days_active.add(time.date())
        day_breakdown[len(days_active)] += 1
    return day_breakdown


def check_invalid_autogen_submissions():
    db = api.api.common.get_conn()
    badteams = set()
    cheaters = []
    for problem in api.problem.get_all_problems():
        good_flags = set()
        if 'autogen' in problem and problem['autogen']:
            correct_flags = db.submissions.find({'pid': problem['pid'], 'correct': True})
            for flag in correct_flags:
                good_flags.add(flag['key'])
            incorrect_flags = db.submissions.find({'pid': problem['pid'], 'correct': False})
            for flag in incorrect_flags:
                if flag['key'] in good_flags:
                    team = api.team.get_team(tid=flag['tid'])
                    solution = db.submissions.find_one({'pid': problem['pid'], 'tid': flag['tid'], 'correct': True})
                    if team['eligible'] and team['tid'] not in badteams:
                        if solution is None:
                            cheaters.append((team['team_name'], get_score(tid=flag['tid']), problem['name'], flag['key']))
                        else:
                            cheaters.append((team['team_name'], get_score(tid=flag['tid']), problem['name'], flag['key'], solution['key']))
                        badteams.add(team['tid'])
    print('\n'.join([str(x) for x in sorted(cheaters, key=lambda x: x[1], reverse=True)]))


def get_review_stats():
    results = []
    problems = api.problem.get_all_problems()
    for p in problems:
        timespent = 0
        enjoyment = 0
        difficulty = 0
        edval = 0
        counter = 0
        for item in api.problem_feedback.get_problem_feedback(pid=p['pid']):
            counter += 1
            metrics = item['feedback']['metrics']
            edval += metrics['educational-value']
            difficulty += metrics['difficulty']
            enjoyment += metrics['enjoyment']
            timespent += item['feedback']['timeSpent']
        if counter > 0:
            results.append({'name': p['name'], 'education': edval/counter, 'difficulty': difficulty/counter,
                            'enjoyment': enjoyment/counter, 'time': timespent/counter, 'votes': counter})
    return results


def print_review_comments():
    problems = api.problem.get_all_problems()
    for p in problems:
        comments = []
        for item in api.problem_feedback.get_problem_feedback(pid=p['pid']):
            comment = item['feedback']['comment']
            if len(comment.strip()) > 0:
                comments.append(comment.strip())
        if len(comments) > 0:
            print("")
            print("")
            print(p['name'])
            print("----------")
            for comment in comments:
                print("'%s'" % comment)