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
    std::cout << "  --regReward <float>      Penalty for changing action" << std::endl;
    std::cout << "                           Default: 0.01" << std::endl;
    std::cout << "  --suffix <int>           Suffix for weights files" << std::endl;
    std::cout << "                           Default: 0" << std::endl;
    std::cout << "  --noOpponent             Sets opponent present flag to false" << std::endl;
    std::cout << "  --eps                    Sets the exploration rate" << std::endl;
    std::cout << "  --lambda                 Lambda to be used in SARSA" << std::endl;
    std::cout << "  --numOpponents           Sets the number of opponents" << std::endl;
    std::cout << "  --load                   If set, load weights from specified weight file" << std::endl;
    std::cout << "  --weightId               Sets the given Id for weight File" << std::endl;
    std::cout << "  --help                   Displays this help and exit" << std::endl;
}

// Returns the reward for SARSA based on current state
inline double getReward(hfo::status_t status) {
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
                  double regReward, int suffix, bool oppPres, double eps, bool load, std::string weightid) {

    // Number of features
    int numF = oppPres ? (8 + 3 * numTMates + 2 * numOpponents) : (3 + 3 * numTMates);
    //numF += 1;  // One feature for previous action
    // Number of actions
    int numA = 5 + numOpponents; //DEF_GOAL+MOVE+GTB+NOOP+RATG+MP(unum)

    // Other SARSA parameters
    eps = 0.01;
    double discFac = 1;
    //double lambda=0.9375; THIS IS THE ACTUAL VALUE
    // double lambda = 0;
    // Tile coding parameter
    double resolution = 0.1;

    double range[numF];
    double min[numF];
    double res[numF];
    for(int i = 0; i < numF; i++) {
        min[i] = -1;
        range[i] = 2;
        res[i] = resolution;
    }

    CMAC *fa = new CMAC(numF, numA, range, min, res);
    char *loadWtFile;
    std::string s = load ? ("weights_" + std::to_string(suffix) +
                            "_" + weightid) : "";
    loadWtFile = &s[0u];
    SarsaAgent *sa = new SarsaAgent(numF, numA, learnR, eps, lambda, fa, loadWtFile, "");

    hfo::HFOEnvironment hfo;
    hfo::status_t status;
    hfo::action_t a;
    int action = -1;
    int prevAction = -1;
    double reward;
    int no_of_offense = numTMates + 1;
    hfo.connectToServer(hfo::HIGH_LEVEL_FEATURE_SET, "../HFO/bin/teams/base/config/formations-dt", port, "localhost", "base_right", false, "");


    int indices[numF];
    double state[numF];

    selectFeatures(indices, numTMates, numOpponents, oppPres);
    for (int episode = 0; episode < (numEpi + numEpiTest); episode++) {
        if ((episode + 1) % 5000 == 0) {
            // Weights file
            char *wtFile;
            std::string s = "weights_" + std::to_string(suffix) +
                            "_" + weightid + "_episode_" + std::to_string(episode + 1);
            wtFile = &s[0u];
            sa -> saveWeights(wtFile);
        }
        // int count = 0;
        status = hfo::IN_GAME;
        action = -1;
        prevAction = -1;
        // int count_steps = 0;
        double unum = -1;
        int num_steps_per_epi = 0;
        while (status == hfo::IN_GAME) {
            num_steps_per_epi++;
            const std::vector<float>& state_vec = hfo.getState();

            if(action != -1) {
                reward = getReward(status);
                // Penalize for changing action
                if(action != prevAction) {
                    reward -= regReward;
                }
                if (episode < numEpi) {
                    sa->update(state, action, reward, discFac); 
                }
                prevAction = action;
            }

            // Fill up state array
            for (int i = 0; i < numF; i++) {
                state[i] = state_vec[indices[i]];
            }

            // Get raw action
            action = sa->selectAction(state);

            // Get hfo::Action
            a = toAction(action, state_vec);
            if (a == hfo::MARK_PLAYER) {
                unum = state_vec[(state_vec.size() - 1 - (action - 5) * 3)];
                hfo.act(a, unum);
            } else {
                hfo.act(a);
            }
            status = hfo.step();
        }
        // End of episode
        if(action != -1) {
            reward = getReward(status);
            if (episode < numEpi) {
                sa->update(state, action, reward, discFac);
            }
            sa->endEpisode();
        }
    }

    delete sa;
    delete fa;
}

int main(int argc, char **argv) {

    int numAgents = 0;
    int numEpisodes = 150000;
    int numEpisodesTest = 10;
    int basePort = 6000;
    double learnR = 0.1;
    double regReward = 0.01;
    int suffix = 0;
    bool opponentPresent = true;
    int numOpponents = 0;
    double eps = 0.01;
    double lambda = 0.0;
    bool load = false;
    std::string weightid;
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
        } else if(param == "--regReward") {
            regReward = atof(argv[++i]);
        } else if(param == "--suffix") {
            suffix = atoi(argv[++i]);
        } else if(param == "--noOpponent") {
            opponentPresent = false;
        } else if(param == "--eps") {
            eps = atoi(argv[++i]);
        } else if(param == "--lambda") {
            lambda = atoi(argv[++i]);
        } else if(param == "--numOpponents") {
            numOpponents = atoi(argv[++i]);
        } else if(param == "--load") {
            load = true;
        } else if(param == "--weightId") {
            weightid = std::string(argv[++i]);
        } else {
            printUsage();
            return 0;
        }
    }
    int numTeammates = numOpponents - 1;
    std::thread agentThreads[numAgents];
    for (int agent = 0; agent < numAgents; agent++) {
        agentThreads[agent] = std::thread(offenseAgent, basePort,
                                          numTeammates, numOpponents, numEpisodes, numEpisodesTest, learnR, lambda,
                                          regReward, agent, opponentPresent, eps, load, weightid);
        sleep(5);
    }
    for (int agent = 0; agent < numAgents; agent++) {
        agentThreads[agent].join();
    }
    return 0;
}

