from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import numpy as np

author = 'YenSheng'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'DominanceGame'
    players_per_group = None
    num_rounds = 500 # a safe number by which game should be over
    REWARD = 1000
    COST = 10
    num_trials = 1


class Subsession(BaseSubsession):
    def creating_session(self):
        group = self.get_groups()[0]  # Get the first (only one) group
        num_players = self.session.num_participants # otree given function
        talents_dist = np.random.randint(0, 10, num_players)
        all_rounds_tournament = group.game_scheduler(num_players, shuffle=False)
        self.session.vars['all_rounds_tournament'] = all_rounds_tournament # add and define a new session level variables
        for id, player in enumerate(self.get_players(), start=1):
            # ??? player or participant?
            player.participant.vars['accounts'] = 0
            player.participant.vars['talents'] = talents_dist[id-1]
            player.participant.vars['records'] = []
            player.participant.vars['ranking'] = []
            player.participant.vars['id'] = id

class Group(BaseGroup):
    game_over = models.BooleanField(initial=False)

    def confirm_game_over(self):
        if self.round_number == Constants.num_trials * (self.session.num_participants - 1):
            self.set_game_over(game_over=True)

    def set_game_over(self, game_over):
        self.game_over = game_over




    def game_scheduler(self, num_of_players, shuffle=False):
        # build players' ids
        player_ids = np.array(list(range(1, num_of_players + 1)))
        if shuffle:
            np.random.shuffle(player_ids)
        if num_of_players % 2 != 0:
            # add a virtual player so that the number of players is a multiple of 2
            player_ids = np.append(player_ids, -1)
            num_of_players += 1
        player_ids = player_ids.reshape(-1,
                                        2)  # -1 automatical calculate the number of rows, 2 means that we always want to 2 columns
        anchor_id = player_ids[0, 0]  # upper left position in the n/2 by 2 matrix
        circle_ids = np.append(player_ids[1:, 0], list(reversed(player_ids[:, 1])))
        id2cirIdx = dict(zip(circle_ids, list(range(len(circle_ids)))))
        cir_real_indices = ([(row, 0) for row in range(1, len(player_ids[1:, 0]) + 1)] +
                            [(row, 1) for row in
                             range(len(player_ids[:, 1]) - 1, -1, -1)])  # "+" is to combine vectors into a list
        cirIdx2realIdx = dict(zip(id2cirIdx.values(), cir_real_indices))

        # use two dicts to update each round scheduled players' ids
        rounds_scheduled_ids = list()
        for round in range(1, len(circle_ids) + 1):
            sheduled_ids = np.zeros(player_ids.shape)
            sheduled_ids[0][0] = anchor_id
            for id in circle_ids:
                i, j = cirIdx2realIdx[id2cirIdx[id]]
                sheduled_ids[i][j] = id
            sheduled_ids = [(int(a_id), int(b_id)) for a_id, b_id in sheduled_ids]
            rounds_scheduled_ids.append(sheduled_ids)
            circle_ids = np.append(circle_ids[-1], circle_ids[:-1])  # this rotates (clockwise) the vector
            id2cirIdx = dict(zip(circle_ids, list(range(num_of_players - 1))))
        return rounds_scheduled_ids

    def match_players(self):
        current_round_num = self.round_number
        all_rounds_tournament = self.session.vars['all_rounds_tournament']
        num_players = self.session.num_participants
        current_round_match = all_rounds_tournament[current_round_num % (num_players - 1)-1]
        for k in current_round_match:
            i,j=k
            player_i = self.get_player_by_id(i)
            player_j = self.get_player_by_id(j)
            player_i.set_opponent(j)
            player_j.set_opponent(i)

    def competition_calculation(self):
        current_round_num = self.round_number
        all_rounds_tournament = self.session.vars['all_rounds_tournament']
        num_players = self.session.num_participants
        current_round_match = all_rounds_tournament[current_round_num % (num_players - 1) - 1]
        for k in current_round_match:
            i, j = k
            player_i = self.get_player_by_id(i)
            player_j = self.get_player_by_id(j)
            performance_i = player_i.efforts/100 * player_i.participant.vars['talents']
            performance_j = player_j.efforts/100 * player_j.participant.vars['talents']
            if performance_i > performance_j:
                player_i.participant.vars['accounts'] += Constants.REWARD - Constants.COST * player_i.efforts
                player_j.participant.vars['accounts'] -= Constants.COST * player_j.efforts
                player_i.participant.vars['records'].append(1)
                player_j.participant.vars['records'].append(0)
            elif performance_i == performance_j:
                player_i.participant.vars['accounts'] += Constants.REWARD/2 - Constants.COST * player_i.efforts
                player_j.participant.vars['accounts'] += Constants.REWARD / 2 - Constants.COST * player_j.efforts
                player_i.participant.vars['records'].append(1/2)
                player_j.participant.vars['records'].append(1/2)
            else:
                player_i.participant.vars['accounts'] -= Constants.COST * player_i.efforts
                player_j.participant.vars['accounts'] += Constants.REWARD - Constants.COST * player_j.efforts
                player_i.participant.vars['records'].append(0)
                player_j.participant.vars['records'].append(1)

    def ranking_calculation(self):
        if self.round_number % (self.session.num_participants - 1) == 0:
            players_records = []
            for i in range(1, self.session.num_participants+1):
                player_i = self.get_player_by_id(i)
                players_records.append(np.mean(player_i.participant.vars['records']))

            sort_raw = sorted(range(len(players_records)), key=lambda k: players_records[k])
            for i in sort_raw:
                player_i = self.get_player_by_id(sort_raw[i]+1)
                player_i.participant.vars['ranking'] = i

class Player(BasePlayer):
    efforts = models.IntegerField(choices=range(0, 101), widget=widgets.Slider)
    opponent = models.IntegerField()

    def get_id(self):
        return self.participant.vars['id']

    def set_opponent(self, rival):
        self.opponent = rival

    def get_opponent(self):
        return self.opponent

    def get_personal_records(self):
        return np.round(np.mean(self.participant.vars['records']), 2)

    def get_personal_ranking(self):
        return self.participant.vars['ranking']

    def get_personal_talents(self):
        return self.participant.vars['talents']


