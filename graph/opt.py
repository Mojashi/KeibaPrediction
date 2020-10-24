import optuna
import numpy as np
import matplotlib.pyplot as plt
import subprocess

def objective(trial):
    ind = trial.suggest_uniform('INDIRECT_COEFF', 0, 1)
    hangen = trial.suggest_uniform('hangen', 0, 1000)
    pace = trial.suggest_uniform('pace', 1, 1000)
    retbound = trial.suggest_uniform('return_bound', 0, 20)
    maxlate = trial.suggest_uniform('max_late', 0, 20)
    proc = subprocess.Popen(['./a.out'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE)
    stdout_value, stderr_value = proc.communicate(b'%f %f %f %f %f\n'%(ind,hangen,pace,retbound,maxlate))
    ret = None
    try:
        ret = int(stdout_value)
    except:
        return None
    return ret
def main():
    study = optuna.Study(
        study_name="graphopt2",
        storage="mysql://keiba@localhost/optuna"
    )

    study.optimize(objective,
                   n_trials=10000,
                   n_jobs=3)
    print(len(study.trials))
    print(study.best_params)


if __name__ == '__main__':
    main()