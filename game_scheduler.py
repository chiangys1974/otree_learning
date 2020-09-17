import numpy as np


def game_scheduler(num_of_players, shuffle=False):
    # build players' ids
    player_ids = np.array(list(range(1, num_of_players + 1)))
    if shuffle:
        np.random.shuffle(player_ids)
    if num_of_players % 2 != 0:
        # add a virtual player so that the number of players is a multiple of 2
        player_ids = np.append(player_ids, -1)
        num_of_players += 1
    print(type(player_ids))
    player_ids = player_ids.reshape(-1, 2) # -1 automatical calculate the number of rows, 2 means that we always want to 2 columns
    anchor_id = player_ids[0, 0] # upper left position in the n/2 by 2 matrix
    circle_ids = np.append(player_ids[1:, 0], list(reversed(player_ids[:, 1])))
    id2cirIdx = dict(zip(circle_ids, list(range(len(circle_ids)))))
    cir_real_indices = ([(row, 0) for row in range(1, len(player_ids[1:, 0]) + 1)] +
                        [(row, 1) for row in range(len(player_ids[:, 1]) - 1, -1, -1)]) # "+" is to combine vectors into a list
    cirIdx2realIdx = dict(zip(id2cirIdx.values(), cir_real_indices))

    # use two dicts to update each round scheduled players' ids
    rounds_scheduled_ids = list()
    for round in range(1, len(circle_ids)+1):
        print(f'--------- ROUND {round} ---------')
        sheduled_ids = np.zeros(player_ids.shape)
        sheduled_ids[0][0] = anchor_id
        for id in circle_ids:
            i, j = cirIdx2realIdx[id2cirIdx[id]]
            sheduled_ids[i][j] = id
        sheduled_ids = [(int(a_id), int(b_id)) for a_id, b_id in sheduled_ids]
        rounds_scheduled_ids.append(sheduled_ids)
        circle_ids = np.append(circle_ids[-1], circle_ids[:-1]) # this rotates (clockwise) the vector
        id2cirIdx = dict(zip(circle_ids, list(range(num_of_players - 1))))
        print(sheduled_ids)

    print(f'--------- RETURN ---------')
    print(rounds_scheduled_ids[0][0][0])
    return rounds_scheduled_ids



def main():
    num_of_players = 6
    all_rounds_tournament = game_scheduler(num_of_players, shuffle=False)


if __name__ == '__main__':
    main()

