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
1. Clone CTF-Dev from GitHub
2. In that directory, `git submodule init`
3. In that directory, `git submodule update`
4. Download VirtualBox (easiest, though others can work)
5. Download Vagrant (vagrantup.com)
6. `vagrant up` in CTF-Dev
7. Wait 20 minutes
8. `vagrant ssh` to connect to the VM
9. Run `devploy` to deploy the development version of the site
10. Go to port 8080 on the Host Machine
11. Remember to always use 127.0.0.1:8080 not localhost:8080
12. Note: The database will not have any problems in it by default. To add the picoCTF 2013 problems to the database, use `python3 ~/api/api_manager.py ~/api/problems/problems.json`

*Warning*: The CTF-Dev repo uses submodules to load in extra code. Submodules are not particularly intuitive and indeed have some unexpected behavior if you have not seen them before. The safest choice is always to edit the submodule repo outside of CTF-Dev as its own separate repo. If you do want to commit from inside CTF-Dev, however, you will need to do `git checkout master` first. Be careful to check that you have indeed done this before commiting something, or it may be difficult to recover your changes.

Contact
------------

We are happy to help but no support is guaranteed.

Authors: Jonathan Burket, Tim Becker, Chris Ganas

Copyright: Carnegie Mellon University

License: MIT

Maintainers: Peter Chapman, Jonathan Burket

Credits: David Brumley, Tim Becker, Chris Ganas, Peter Chapman, Jonathan Burket

Email: peter@cmu.edu, jburket@cmu.edu

