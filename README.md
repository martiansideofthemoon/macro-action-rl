Macro Actions for Reinforcement Learning
========================================

This is the repository for a course project in Reinforcement Learning ([CS747](https://www.cse.iitb.ac.in/~shivaram/teaching/cs747-a2017/)) by [Kalpesh Krishna](https://github.com/martiansideofthemoon/), [Vihari Piratla](https://github.com/vihari) and [Varun Bhatt](https://github.com/virtualgod).

## Algorithms

We implement five macro-action algorithms on the HFO framework to learn defensive strategies.

* **Decision Interval SARSA** - Located in `di_sarsa`, this algorithm repeats the same action for a fixed number of steps before a SARSA update and a change in action.
* **FiGAR SARSA** - Located in `figar_sarsa`, this is a SARSA version of the Fine Grained Action Repetition framework, described in an ICLR 2017 [paper](https://arxiv.org/abs/1702.06054).
* **Reward Regularization** - Located in `reg_sarsa`, this algorithm penalizes a agent whenever it changes its action. This fixed penalty is directly deduced from the received reward.
* **Augmented Action Space** - Located in `action_space_sarsa`, this algorithm is a SARSA version of an AAAI paper, [Dynamic Action Repetition for Deep Reinforcement Learning](https://www.aaai.org/ocs/index.php/AAAI/AAAI17/paper/viewFile/14866/14384).
* **Conditional FiGAR SARSA** - Located in `conditional_figar_sarsa`, this algorithm modifies **FiGAR SARSA** and conditions the dynamic interval decision on the previously taken action.

## Setup
This project uses the [Half-Field Offense](https://github.com/LARG/HFO) framework as a testbed. Make sure your system satisfies the requirements needed by this framework. Start in the root directory of this project.
````
git clone https://github.com/LARG/HFO
cd HFO
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=RelwithDebInfo ..
make -j4
make install
cd ../..
./build.sh
````

Set `server_wait_seconds` to 100 in `HFO/bin/teams/base/config/player.conf`.

If there is an error with rcssserver, clone [mhauskn/rcssserver](https://github.com/mhauskn/rcssserver) and install using

````
./configure --with-boost-libdir=/usr/lib/x86_64-linux-gnu
make
sudo make install
````
Then change line 67 in `HFO/bin/HFO` from `serverCommand = os.path.join(binary_dir, SERVER_BIN)` to `serverCommand = SERVER_BIN`.

## Running

You can run the bash scripts in the `schedulers` directory for each of the five algorithms. These scripts run a 2v2 scenario with one defense agent being trained. For example,
````
mkdir logs
./schedulers/figar_sarsa.sh
````
You will find the results in the newly created `logs` directory.

Scripts to run a 3v3 scenario with two defense agents being trained can be found in `schedulers3v3` directory.

## Report

You can find our final project report in `report/report.pdf`. The empirical results have been added to `report/report.org` and plots to `report/plots/`.
