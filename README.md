CTF-Platform 2
==============

The CTF-Platform is the infrastructure on which picoCTF runs. The 
platform is designed to be easily adapted to other CTF or programming 
competitions.

CTF-Platform 2 targets Ubuntu 14.04 LTS but should work on just about 
any "standard" Linux distribution. It would probably even work on 
Windows. MongoDB must be installed; all default configurations should 
work.

Setting Up
------------
1. Download VirtualBox (easiest, though others can work)
2. Download Vagrant (vagrantup.com)
3. `vagrant up` inside the repo
4. Wait 20 minutes
5. `vagrant ssh` to connect to the VM
6. Run `devploy` to deploy the development version of the site
7. Go to port 8080 on the Host Machine
8. Remember to always use 127.0.0.1:8080 not localhost:8080

*Note*: The competition has two modes: competition active and competition inactive. In inactive mode, there are no problems and only registration is available. To change what mode the competition is in, edit api/api/config.py and change the competition dates such that the current date is either inside or outside the range of the competition dates.


Loading the Example Problems (In the vagrant VM)
------------
1. Run `cd ~/api`
2. Run `python3 api_manager.py -v problems load /vagrant/example_problems/ graders/ ../problem_static/`
3. Run `python3 api_manager.py autogen build 100`
4. Run `devploy`


Creating Problems
------------
There are two types of problems supported by this framework: *basic* problems, and *auto-generated* problems. Auto-generated problems allow for different users to receive different versions of the same problem. Basic problems have only one version. In this section we will discuss adding basic problems. Several example problems are included under the *example_problems* directory.

Every basic problem needs two components: a *problem.json* file and a *grader* directory containing a grading script. A *problem.json* file should look like this:

    {"name": "Problem Name",
     "score": 10,
     "category": "Category Name",
     "grader": "misc/myproblem/grader.py",
     "description": "Problem text. HTML can be used here.",
     "threshold": 0,
     "weightmap": {},
     "hint": "Hint text. HTML can be used here"}

A grading script should look like this:

    def grade(arg, key):
        if "this_is_the_flag" in key:
            return True, "Correct"
        else:
            return False, "Incorrect"

Note that the problem loading script (`api_manager.py problems load`) makes a number of assumptions about the folder structure used to hold your problems. Suppose you want to create a new problem *My Problem* and you are storing all of your problems in ~/problems. First we make a directory for our problem, such as `/problems/misc/myproblem`. Now we place our *problem.json* file at `/problems/misc/myproblem/problem.json` and our grading script at `/problems/misc/myproblem/grader/grader.py`. Now we double check that our "grader" path in *problem.json* points to the grader. Note that this path is NOT an absolute path. It instead has the following format: if our grader is at `[problem directory]/[path to problem in problem directory]/grader/[grader name]`, then the "grader" path should be set to `[path to problem in problem directory]/[grader name]`. Thus, for `/problems/misc/myproblem/grader/grader.py`, we use `misc/myproblem/grader.py`.

The "threshold" and "weightmap" fields are used to manage problem unlocking. If you would like a problem to always be available, set "threshold" to 0 and "weightmap" to {}. Suppose we have four problems "A", "B", "C", and "D". If we want to make "D" unlock if any 2 of "A", "B", or "C" are solved, we set the "weightmap" to `{"A": 1, "B": 1, "C": 1}` since all these problems are weighted equally and "threshold" to 2, since we want to unlock the problem when any two problems are solved.

Some problems need to provide additional files for the user to view or download (binaries, encrypted messages, images, etc.). To add static files to your problem, add a *static* folder in the directory for that problem (`/problems/misc/myproblem/static/`, for example) and place any files in that directory that you want to serve statically. Then, in your problem description (or hint), you can link to this file using the URL `/problem-static/[path to problem in problems directory]/[file name]`. Look at the example problem 'Sdrawkcab' to see this in action.


Contact
------------

We are happy to help but no support is guaranteed.

Authors: Jonathan Burket, Tim Becker, Chris Ganas

Copyright: Carnegie Mellon University

License: MIT

Maintainers: Peter Chapman, Jonathan Burket

Credits: David Brumley, Tim Becker, Chris Ganas, Peter Chapman, Jonathan Burket

Email: peter@cmu.edu, jburket@cmu.edu

