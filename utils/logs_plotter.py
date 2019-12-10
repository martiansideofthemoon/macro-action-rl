import glob
import numpy as np
import matplotlib.pyplot as plt
import re
from collections import defaultdict

trials_re = re.compile(r"Trials\s*:\s(\d+)\s")
goals_re = re.compile(r"Trials\s*:\s(\d+)\s")
defense_re = re.compile(r"Defense\sCaptured\s*:\s(\d+)\s")
ball_oob_re = re.compile(r"Balls\sOut\sof\sBounds\s*:\s(\d+)\s")
out_of_time_re = re.compile(r"Out\sof\sTime\s*:\s(\d+)\s")


def get_episode_number(filename):
    return int(filename[filename.index("episode_") + len("episode_"):filename.index(".log")])


class Experiment(object):
    def __init__(self, file_pattern, string):
        self.file_pattern = file_pattern
        self.experiment_string = string

        files = glob.glob(file_pattern)

        files.sort(key=lambda x: get_episode_number(x))

        self.episode_scores = defaultdict(list)

        for file in files:
            ep_number = get_episode_number(file)

            with open(file, "r") as f:
                data = f.read().strip()

            num_trials = int(re.findall(trials_re, data)[0])
            assert num_trials == 2000

            num_defenses = int(re.findall(defense_re, data)[0])
            num_oob = int(re.findall(ball_oob_re, data)[0])
            num_out_of_time = int(re.findall(out_of_time_re, data)[0])

            score = float(num_defenses + num_oob + num_out_of_time) / float(num_trials)

            self.episode_scores[ep_number].append(score)

    def return_scores(self):
        episode_nums = sorted(list(self.episode_scores.keys()))
        score_means = []
        score_errors = []
        for ep_num in episode_nums:
            curr_scores = self.episode_scores[ep_num]
            score_means.append(np.mean(curr_scores))
            score_errors.append(np.std(curr_scores) / np.sqrt(len(score_means)))
        return episode_nums, score_means, score_errors, self.experiment_string


patterns = [
    ("logs3v3_test/server_di_sarsa_step_1_lambda_0.500000_*", "step = 1"),
    ("logs3v3_test/server_di_sarsa_step_2_lambda_0.500000_*", "step = 2"),
    ("logs3v3_test/server_di_sarsa_step_4_lambda_0.500000_*", "step = 4"),
    ("logs3v3_test/server_di_sarsa_step_8_lambda_0.500000_*", "step = 8"),
    ("logs3v3_test/server_di_sarsa_step_16_lambda_0.500000_*", "step = 16"),
    ("logs3v3_test/server_di_sarsa_step_32_lambda_0.500000_*", "step = 32"),
]

experiments = [Experiment(pattern, string) for pattern, string in patterns]

f = plt.figure()

for exp in experiments:
    x, y, y_error, label = exp.return_scores()
    plt.errorbar(x=x, y=y, yerr=y_error, label=label)

plt.ylabel("Percentage Captured")
plt.xlabel("Number of Episodes")

plt.legend(loc="upper right", ncol=2)

plt.show()
f.savefig("foo.pdf", bbox_inches='tight')
