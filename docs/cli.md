# Command Line Interface

To evaluate the experiments, first set up the environment:
```bash
source setupenv
```

Then the `liver` command will be present and you can run `liver -h` to see what it does:
```bash
$ liver -h
usage: liver [-h] --experiment {1,2,3} [--debug]
             [--learners-group {logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} [{logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} ...]]
             [--config {default,global,experiment1,experiment2,experiment3}] [--plot-only]

options:
  -h, --help            show this help message and exit
  --experiment {1,2,3}
  --debug               Enable debug logging
  --learners-group {logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} [{logistic-regression,random-forest,tree,gradient-boosting,neural-network,svm} ...]
                        Run specific family(ies) of learners.
  --config {default,global,experiment1,experiment2,experiment3}
                        Configuration to use for the experiment
  --plot-only           Plot only on already existing results.
```

To check the generated results/report, run:
```bash
wslview results/experiment<experiment>-<config>.csv
wslview reports/experiment<experiment>-<config>.html
```
