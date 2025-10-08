![lemming](https://64.media.tumblr.com/e94d842cfaddc4e400df2a08a167982b/tumblr_inline_pjwpg3WVNJ1t0ktpa_500.png)

*Lemmings is a [1991 video game](https://en.wikipedia.org/wiki/Lemmings_(video_game)) where the player try to herd small animals, the "lemmings" out of a a 2D puzzle. Lemmings are clueless about their surroundings, walk blindly, and will eventually fall, burn, be crushed, ... well die, unless the player personally take care of them. The "Lemmings Jobs ", introduced here, are the same : by nature, these unsupervised job submission often end up in dramatic failures. Human oversight is compulsory when you are dealing with chained runs.*

## Lemmings

### Idea

Lemmings  is an open-source code designed to simplify the submission of multiple inter-dependent jobs on the schedulers of HPC clusters.
While originally developed within the context of Computational Fluid Dynamics (CFD) applications, it is adapted to many recursive jobs. A farming mode is present to help the replication of these recursive jobs for a parametric study.

### Installation

Lemmings is open-source and can be pip-installed :

```bash
pip install lemmings-hpc
```

### End user POV


The end-user of lemmings is someone making a lot of simulations with a repetitive pattern.
This repetition (eg. resubmit the job until simulated time reaches 1ms) is automated by a lemmings "workflow", a python file gathering all the logic of the application. This "workflow" was created by a super user using lemmings.

Here The end-user (John Doe) adds the workflow (sandcastle) file where he usually launches the run, then run the `lemmings run` command:


```
>lemmings run --machine-file sandbox.yml --job-prefix funtask sandcastle
INFO - 
##############################
Starting Lemmings 0.8.0...
##############################

INFO -     Job name     :funtask_PAJI77
INFO -     Loop         :1
INFO -     Status       :start
INFO -     Worflow path :/Users/johndoe/productionpath/sandcastle.py
INFO -     Imput path   :/Users/johndoe/productionpath/sandcastle.yml
INFO -     Machine path :/Users/johndoe/productionpath/sandbox.yml
INFO -     Farming mode :False
INFO -     Lemmings START (1/3)
INFO -          Check on startTrue (False -> Exit)
INFO -          Prior to job
INFO -     Lemmings SPAWN (2/3)
INFO -          Prepare run
INFO -          Submit batch 74148 
INFO -          Submit batch post job 74149
```

This execution will be called `funtask_PAJI77` and will automatically submit runs through the job schedulers. On the job scheduler, he will find something like

```>qstat -u johndoe
+----------------+---------------+-------+----------+-------------------+---------+
|    job name    |     queue     | pid   |  state   |    last update    |  after  |
+----------------+---------------+-------+----------+-------------------+---------+
| funtask_PAJI77 |  long00:00:30 | 74148 |   done   | 06/13/22 15:22:52 |    -    |
| funtask_PAJI77 | short00:00:10 | 74149 |  running | 06/13/22 15:22:53 |  74148  |
+----------------+---------------+-------+----------+-------------------+---------+
```

Here jobs `funtask_PAJI77_74148` and `funtask_PAJI77_74149` are the two first dependent jobs of the workflow, but more will come.
The decision to re-submit and the creation of the next job will be handled by `funtask_PAJI77_74149` after completion. *Therefore Lemmings does not "book" consecutive PID on start, only the next jobs are queued*. 

Finally lemmings is not moving/hiding log files automatically. By actively limiting such "black magic", it enforces an experience similar to manual re-submission

### Creating a workflow

A super-user creates a workflow by injecting code into some parts of a baseline Loop.
The default, simplified, lemmings job follows this algorithm:

```
                +-----------+                     +------------+True  
Start---------->|Prepare Run+--->Job submission--->Check on end+----------->Happy
            ^   +-----------+                     +------+-----+             End
            |                                            |
            |                                            |False
            |                                            |
            |                                            |
            +--------------------------------------------+                          
```

By adding code to **Prepare Run** phase (updates of input file) and to **Check on end** (when to stop the job), the super-user can customize it to his needs. Follows the HowTos for an extended explanation.


### Resources

Lemmings documentation can be found following this link : [lemmings documentation](https://lemmings.readthedocs.io/en/latest/)

### Acknowledgements

Lemmings is a service created in the [EXCELLERAT Center Of Excellence](https://www.excellerat.eu/wp/) and is continued as part of the [COEC Center Of Excellence](https://coec-project.eu/). Both projects are funded by the European community.


![logo](https://www.excellerat.eu/wp-content/uploads/2020/04/excellerat_logo.png)

![logo](https://www.hpccoe.eu/wp-content/uploads/2020/10/cnmlcLiO_400x400-e1604915314500-300x187.jpg)
