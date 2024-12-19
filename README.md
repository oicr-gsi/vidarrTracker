# vidarrTracker

A simple logger of workflow deployment to vidarr instancesa

# A two-step process

* First, we interrogate vidarr instances with some curl commands
* Next, we generate a HTML report page with updates listed for all vidarr instances

# Running using regular intervals

The main purpose of vidarrTracker is to keep a log of deployment events so that
we could monitor and review the process of bringing into vidarr new workflows and
updates to the existing ones (version increments).

![prototype_screen](images/vidarrTracker_screenshot.png)
