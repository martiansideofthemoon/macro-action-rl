import glob
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import re
from collections import defaultdict

trials_re = re.compile(r"Trials\s*:\s(\d+)\s")
goals_re = re.compile(r"Trials\s*:\s(\d+)\s")
defense_re = re.compile(r"Defense\sCaptured\s*:\s(\d+)\s")
ball_oob_re = re.compile(r"Balls\sOut\sof\sBounds\s*:\s(\d+)\s")
out_of_time_re = re.compile(r"Out\sof\sTime\s*:\s(\d+)\s")

matplotlib.rcParams.update({'font.size': 14})


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

            try:
                num_trials = int(re.findall(trials_re, data)[0])
            except:
                print(file)
                continue

            try:
                assert num_trials == 2000
            except:
                print(file)
                continue

            num_defenses = int(re.findall(defense_re, data)[0])
            num_oob = int(re.findall(ball_oob_re, data)[0])
            num_out_of_time = int(re.findall(out_of_time_re, data)[0])

            score = float(num_defenses + num_oob + num_out_of_time) / float(num_trials)

            self.episode_scores[ep_number].append(score)

        print("%s = %s" % (file_pattern, [len(x) for _, x in self.episode_scores.items()]))

    def return_scores(self):
        episode_nums = sorted(list(self.episode_scores.keys()))
        score_means = []
        score_errors = []
        for ep_num in episode_nums:
            curr_scores = self.episode_scores[ep_num]
            score_means.append(np.mean(curr_scores))
            score_errors.append(np.std(curr_scores) / np.sqrt(len(curr_scores)))
        return episode_nums, score_means, score_errors, self.experiment_string


MODE = "2v2"

if MODE == "3v3":
    # patterns = [
    #     ("logs3v3_test/server_di_sarsa_step_1_lambda_0.500000_*", "SARSA"),
    #     ("logs3v3_highlr_test/server_di_sarsa_step_1_lambda_0.500000_learnRate_0.010000*", "SARSA, LR = 0.01"),
    #     ("logs3v3_test/server_di_sarsa_step_128_lambda_0.500000_*", "DI-SARSA (step = 128)"),
    #     ("logs3v3_highlr_test/server_di_sarsa_step_16_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 16) LR = 0.01"),
    #     ("logs3v3_highlr_test/server_di_sarsa_step_32_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 32) LR = 0.01"),
    #     ("logs3v3_highlr_test/server_di_sarsa_step_48_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 48) LR = 0.01"),
    #     ("logs3v3_highlr_test/server_di_sarsa_step_64_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 64) LR = 0.01"),
    #     ("logs3v3_highlr_test/server_di_sarsa_step_128_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 128) LR = 0.01"),
    #     # ("logs3v3_test/server_conditional_figar_sarsa_lambda_0.800000_*", "CONDITIONAL-FIGAR-SARSA"),
    # ]

    patterns = [
        ("logs3v3_test/server_di_sarsa_step_1_lambda_0.500000_*", "SARSA"),
        # ("logs3v3_test/server_di_sarsa_step_2_lambda_0.500000_*", "step = 2"),
        # ("logs3v3_test/server_di_sarsa_step_4_lambda_0.500000_*", "step = 4"),
        # ("logs3v3_test/server_di_sarsa_step_8_lambda_0.500000_*", "step = 8"),
        # ("logs3v3_test/server_di_sarsa_step_16_lambda_0.500000_*", "step = 16"),
        # ("logs3v3_test/server_di_sarsa_step_32_lambda_0.500000_*", "step = 32"),
        # ("logs3v3_test/server_di_sarsa_step_48_lambda_0.500000_*", "step = 48"),
        # ("logs3v3_test/server_di_sarsa_step_64_lambda_0.500000_*", "step = 64"),
        ("logs3v3_highlr_test/server_di_sarsa_step_32_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 32)"),
        ("logs3v3_highlr_test/server_di_sarsa_step_64_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 64)"),
        ("logs3v3_highlr_test/server_di_sarsa_step_128_lambda_0.500000_learnRate_0.010000*", "DI-SARSA (step = 128)"),
        ("logs3v3_highlr_test/server_figar_sarsa_lambda_0.500000_*", "FIGAR-SARSA"),
        # ("logs3v3_test/server_conditional_figar_sarsa_lambda_0.800000_*", "CONDITIONAL-FIGAR-SARSA"),
    ]
else:
    patterns = [
        ("logs3_test/server_di_sarsa_step_1_lambda_0.800000_*", "SARSA"),
        ("logs3_test/server_di_sarsa_step_2_lambda_0.800000_*", "DI-SARSA (step = 2)"),
        ("logs3_test/server_di_sarsa_step_4_lambda_0.800000_*", "DI-SARSA (step = 4)"),
        ("logs3_test/server_di_sarsa_step_8_lambda_0.800000_*", "DI-SARSA (step = 8)"),
        ("logs3_test/server_di_sarsa_step_16_lambda_0.800000_*", "DI-SARSA (step = 16)"),
        ("logs3_test/server_di_sarsa_step_32_lambda_0.800000_*", "DI-SARSA (step = 32)"),
        ("logs3_test/server_di_sarsa_step_48_lambda_0.800000_*", "DI-SARSA (step = 48)"),
        ("logs3_test/server_di_sarsa_step_64_lambda_0.800000_*", "DI-SARSA (step = 64)"),
        ("logs3_test/server_di_sarsa_step_128_lambda_0.800000_*", "DI-SARSA (step = 128)"),
        ("logs3_test/server_di_sarsa_step_256_lambda_0.800000_*", "DI-SARSA (step = 256)"),
        ("logs3_test/server_figar_sarsa_lambda_0.800000_*", "FIGAR-SARSA"),
        # ("logs3_test/server_action_space_sarsa_lambda_0.800000_*", "Action Space Sarsa"),
        # ("logs3_test/server_reg_sarsa_lambda_0.800000_*", "Regularized Sarsa"),
    ]

experiments = [Experiment(pattern, string) for pattern, string in patterns]

f = plt.figure()

for exp in experiments:
    x, y, y_error, label = exp.return_scores()
    print("%s = %.4f +/- %.4f" % (exp.experiment_string, y[0], y_error[0]))
    plt.errorbar(x=x, y=y, yerr=y_error, label=label)

if MODE == "3v3":
    plt.errorbar(x=x, y=[0.199 for _ in x], yerr=[0.008 for _ in x], label="RANDOM")
    plt.errorbar(x=x, y=[0.61 for _ in x], yerr=[0.002 for _ in x], label="HELIOS")
else:
    plt.errorbar(x=x, y=[0.152 for _ in x], yerr=[0.002 for _ in x], label="RANDOM")
    plt.errorbar(x=x, y=[0.283 for _ in x], yerr=[0.005 for _ in x], label="HELIOS")

plt.ylabel("Fraction Captured")
plt.xlabel("Number of Episodes")

plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
           mode="expand", borderaxespad=0, ncol=2)

# plt.legend(loc="upper right", ncol=2)


plt.show()
f.savefig("foo.pdf", bbox_inches='tight')
