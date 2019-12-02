#include <iostream>
#include <vector>
#include <HFO.hpp>
#include <cstdlib>
#include <thread>
#include "SarsaAgent.h"
#include "CMAC.h"
#include <unistd.h>

// Before running this program, first Start HFO server:
// $./bin/HFO --offense-agents numAgents

std::vector<int> process_csv(std::string freq_set) {
    std::vector<int> vect;
    std::stringstream ss(freq_set);
    int i;
    while (ss >> i)
    {
        vect.push_back(i);
        if (ss.peek() == ',')
            ss.ignore();
    }
    return vect;
}

void printUsage() {
    std::cout << "Usage:123 ./high_level_sarsa_agent [Options]" << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  --numAgents <int>        Number of SARSA agents" << std::endl;
    std::cout << "                           Default: 0" << std::endl;
    std::cout << "  --numEpisodes <int>      Number of episodes to run" << std::endl;
    std::cout << "                           Default: 10" << std::endl;
    std::cout << "  --numEpisodesTest <int>  Number of episodes to test" << std::endl;
    std::cout << "                           Default: 10" << std::endl;
    std::cout << "  --basePort <int>         SARSA agent base port" << std::endl;
    std::cout << "                           Default: 6001" << std::endl;
    std::cout << "  --learnRate <float>      Learning rate of SARSA agents" << std::endl;
    std::cout << "                           Range: [0.0, 1.0]" << std::endl;
    std::cout << "                           Default: 0.1" << std::endl;
    std::cout << "  --suffix <int>           Suffix for weights files" << std::endl;
    std::cout << "                           Default: 0" << std::endl;
    std::cout << "  --noOpponent             Sets opponent present flag to false" << std::endl;
    std::cout << "  --eps                    Sets the exploration rate" << std::endl;
    std::cout << "  --numOpponents           Sets the number of opponents" << std::endl;
    std::cout << "  --load                   If set, load weights from specified weight file" << std::endl;
    std::cout << "  --weightId               Sets the given Id for weight File" << std::endl;
    std::cout << "  --help                   Displays this help and exit" << std::endl;
    std::cout << "  --freq_set               comma separated list of frequencies" << std::endl;
}

// Returns the reward for SARSA based on current state
double getReward(hfo::status_t status) {
    double reward;
    if (status == hfo::GOAL) reward = -1;
    else if (status == hfo::CAPTURED_BY_DEFENSE) reward = 1;
    else if (status == hfo::OUT_OF_BOUNDS) reward = 1;
    else reward = 0;
    return reward;
}

// Fill state with only the required features from state_vec
void selectFeatures(int* indices, int numTMates, int numOpponents, bool oppPres) {

    int stateIndex = 0;

    // If no opponents ignore features Distance to Opponent
    // and Distance from Teammate i to Opponent are absent
    int tmpIndex = oppPres ? (9 + 3 * numTMates) : (9 + 2 * numTMates);

    int numF = 10 + 6 * numTMates + 3 * numOpponents;
    for(int i = 0; i < numF; i++) {
        // Ignore first six featues
        if(i == 5 || i == 8) continue;
        else if(i > 9 && i <= 9 + numTMates) continue; // Ignore Goal Opening angles, as invalid
        else if(i <= 9 + 3 * numTMates && i > 9 + 2 * numTMates) continue; // Ignore Pass Opening angles, as invalid
        // Ignore Uniform Number of Teammates and opponents
        int temp =  i - tmpIndex;
        if(temp > 0 && (temp % 3 == 0) )continue;
        //if (i > 9+6*numTMates) continue;
        indices[stateIndex] = i;
        stateIndex++;
    }
}

// Convert int to hfo::Action
hfo::action_t toAction(int action, const std::vector<float>& state_vec) {
    hfo::action_t a;
    switch (action) {
    case 0:
        a = hfo::MOVE;
        break;
    case 1:
        a = hfo::REDUCE_ANGLE_TO_GOAL;
        break;
    case 2:
        a = hfo::GO_TO_BALL;
        break;
    case 3:
        a = hfo::NOOP;
        break;
    case 4:
        a = hfo::DEFEND_GOAL;
        break;
    default :
        a = hfo::MARK_PLAYER;
        break;
    }
    return a;
}

void offenseAgent(int port, int numTMates, int numOpponents, int numEpi, int numEpiTest, double learnR, double lambda,
                  int suffix, bool oppPres, std::vector<int> frequencies, double eps, bool load, std::string weightid) {

    // Number of features
    int numF = oppPres ? (8 + 3 * numTMates + 2 * numOpponents) : (3 + 3 * numTMates);
    // Number of actions
    int numA = 5 + numOpponents; //DEF_GOAL+MOVE+GTB+NOOP+RATG+MP(unum)

    // Other SARSA parameters
    eps = 0.01;
    double discFac = 1;
    //double lambda=0.9375; THIS IS THE ACTUAL VALUE
    // Tile coding parameter
    double resolution = 0.1;

    double range[numF];
    double min[numF];
    double res[numF];
    double range1[numF + 1];
    double min1[numF + 1];
    double res1[numF + 1];
    for(int i = 0; i < numF; i++) {
        min[i] = -1;
        range[i] = 2;
        res[i] = resolution;
        min1[i] = -1;
        range1[i] = 2;
        res1[i] = resolution;
    }
    min1[numF] = 0;
    range1[numF] = numA;
    res1[numF] = resolution;

    // This is for the original action space
    CMAC *fa_action = new CMAC(numF, numA, range, min, res);
    char *loadWtFile1;
    std::string s1 = load ? ("weights_act_" + std::to_string(suffix) +
                            "_" + weightid) : "";
    loadWtFile1 = &s1[0u];
    SarsaAgent *sa_action = new SarsaAgent(numF, numA, learnR, eps, lambda, fa_action, loadWtFile1, "");

    // This is for the original action space
    CMAC *fa_freq = new CMAC(numF + 1, frequencies.size(), range1, min1, res1);
    char *loadWtFile2;
    std::string s2 = load ? ("weights_freq_" + std::to_string(suffix) +
                            "_" + weightid) : "";
    loadWtFile2 = &s2[0u];
    SarsaAgent *sa_freq = new SarsaAgent(numF + 1, frequencies.size(), learnR, eps, lambda, fa_freq, loadWtFile2, "");

    hfo::HFOEnvironment hfo;
    hfo::status_t status;
    hfo::action_t a;
    double state[numF];
    double state1[numF + 1];
    int indices[numF];

    selectFeatures(indices, numTMates, numOpponents, oppPres);

    int action = -1;
    int action_freq = -1;
    double reward;
    hfo.connectToServer(hfo::HIGH_LEVEL_FEATURE_SET, "../HFO/bin/teams/base/config/formations-dt", port, "localhost", "base_right", false, "");


    for (int episode = 0; episode < (numEpi + numEpiTest); episode++) {
        if ((episode + 1) % 5000 == 0) {
            // Weights file
            char *wtFile1, *wtFile2;
            std::string s1 = "weights_act_" + std::to_string(suffix) +
                            "_" + weightid + "_episode_" + std::to_string(episode + 1);
            std::string s2 = "weights_freq_" + std::to_string(suffix) +
                            "_" + weightid + "_episode_" + std::to_string(episode + 1);
            wtFile1 = &s1[0u];
            wtFile2 = &s2[0u];
            sa_action -> saveWeights(wtFile1);
            sa_freq -> saveWeights(wtFile2);
        }
        int count = 0;
        status = hfo::IN_GAME;
        action = -1;
        action_freq = -1;
        int count_steps = 0;
        double unum = -1;
        int num_steps_per_epi = 0;
        int step = 1;

        while (status == hfo::IN_GAME) {
            num_steps_per_epi++;
            if (action_freq != -1) {
                step = frequencies[action_freq];
            }
            const std::vector<float>& state_vec = hfo.getState();

            if (count_steps != step && action >= 0 && (a != hfo :: MARK_PLAYER ||  unum > 0)) {
                count_steps ++;
                if (a == hfo::MARK_PLAYER) {
                    hfo.act(a, unum);
                } else {
                    hfo.act(a);
                }
                status = hfo.step();
                continue;

            } else {
                count_steps = 0;
            }

            if(action != -1 && action_freq != -1) {
                reward = getReward(status);
                if (episode < numEpi) {
                    sa_action->update(state, action, reward, discFac);
                    sa_freq->update(state1, action_freq, reward, discFac);
                }
            }

            // Fill up state array
            for (int i = 0; i < numF; i++) {
                state[i] = state_vec[indices[i]];
                state1[i] = state_vec[indices[i]];
            }

            // Get raw action
            action = sa_action->selectAction(state);

            state1[numF] = action;
            action_freq = sa_freq->selectAction(state1);

            // Get hfo::Action
            a = toAction(action, state_vec);
            if (a == hfo::MARK_PLAYER) {
                unum = state_vec[(state_vec.size() - 1 - (action - 5) * 3)];
                hfo.act(a, unum);
            } else {
                hfo.act(a);
            }
            count_steps++;
            status = hfo.step();
        }
        // End of episode
        if(action != -1) {
            reward = getReward(status);
            if (episode < numEpi) {
                sa_action->update(state, action, reward, discFac);
                sa_freq->update(state1, action_freq, reward, discFac);
            }
            sa_action->endEpisode();
            sa_freq->endEpisode();
        }
    }
    delete sa_action;
    delete sa_freq;
    delete fa_action;
    delete fa_freq;
}

int main(int argc, char **argv) {
    double lambda = 0;
    int numAgents = 0;
    int numEpisodes = 10;
    int numEpisodesTest = 10;
    int basePort = 6000;
    double learnR = 0.1;
    int suffix = 0;
    bool opponentPresent = true;
    int numOpponents = 0;
    double eps = 0.01;
    bool load = false;
    std::string weightid;
    std::string freq_set = "1,2,4,8,16,32,64";
    for (int i = 0; i < argc; i++) {
        std::string param = std::string(argv[i]);
        std::cout << param << "\n";
    }
    for(int i = 1; i < argc; i++) {
        std::string param = std::string(argv[i]);
        if(param == "--numAgents") {
            numAgents = atoi(argv[++i]);
        } else if(param == "--numEpisodes") {
            numEpisodes = atoi(argv[++i]);
        } else if(param == "--numEpisodesTest") {
            numEpisodesTest = atoi(argv[++i]);
        } else if(param == "--basePort") {
            basePort = atoi(argv[++i]);
        } else if(param == "--learnRate") {
            learnR = atof(argv[++i]);
            if(learnR < 0 || learnR > 1) {
                printUsage();
                return 0;
            }
        } else if(param == "--suffix") {
            suffix = atoi(argv[++i]);
        } else if(param == "--noOpponent") {
            opponentPresent = false;
        } else if(param == "--eps") {
            eps = atoi(argv[++i]);
        } else if(param == "--numOpponents") {
            numOpponents = atoi(argv[++i]);
        } else if(param == "--lambda") {
            lambda = atoi(argv[++i]);
        } else if(param == "--load") {
            load = true;
        } else if(param == "--weightId") {
            weightid = std::string(argv[++i]);
        } else if(param == "--freq_set") {
            freq_set = std::string(argv[++i]);
        } else {
            printUsage();
            return 0;
        }
    }

    std::vector<int> frequencies = process_csv(freq_set);

    int numTeammates = numOpponents - 1;
    std::thread agentThreads[numAgents];
    for (int agent = 0; agent < numAgents; agent++) {
        agentThreads[agent] = std::thread(offenseAgent, basePort,
                                          numTeammates, numOpponents, numEpisodes, numEpisodesTest, learnR, lambda,
                                          agent, opponentPresent, frequencies, eps, load, weightid);
        sleep(5);
    }
    for (int agent = 0; agent < numAgents; agent++) {
        agentThreads[agent].join();
    }
    return 0;
}

