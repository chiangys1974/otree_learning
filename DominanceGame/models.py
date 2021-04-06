from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import numpy as np
from random import shuffle

author = 'YenSheng'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'DominanceGame'
    players_per_group = None
    num_rounds = 100 # a safe number by which game should be over
    REWARD = 20
    EFFORTS = 10
    num_trials = 4 # iterations of the tournament

class Subsession(BaseSubsession):
    def creating_session(self):
        if self.round_number == 1:
            group = self.get_groups()[0]  # Get the first (only one) group
            num_players = self.session.num_participants  # otree given function
            if self.session.config['talent_variation'] == '低' :
                talents_dist = range(1, 11, 2) #np.random.randint(0, 10, num_players)
            else :
                talents_dist = range(1, 31, 6)

            print(talents_dist)
            print(type(talents_dist[0]))
            for id, player in enumerate(self.get_players(), start=1):
                player.participant.vars['accounts'] = 0
                player.participant.vars['talents'] = int(talents_dist[id - 1])
                player.talents = player.participant.vars['talents']
                player.participant.vars['records'] = []
                player.participant.vars['ranking'] = []
                player.participant.vars['id'] = id
                player.participant.vars['winning_rates'] = []
            self.session.vars['all_rounds_tournament'] = dict()
            sess_size2splits = {
                4:   [4],
                6:   [6],
                8:   [4, 4],
                10:  [4, 6],
                12:  [4, 4, 4],
                14:  [4, 4, 6],
                16:  [4, 6, 6],
                18:  [6, 6, 6],
                20:  [4, 4, 6, 6],
            }
            players_id = list(range(1, num_players + 1))
            new_structure = list()
            shuffle(players_id)
            self.session.vars['player_id_list'] = players_id
            cur_index = 0
            n_splits = sess_size2splits[num_players] # gets the structure of grouping defined above e.g. [4,4,6,6]
            self.session.vars['group_split'] = n_splits
            self.session.vars['new_id_to_ori_id'] = dict()
            for group_id, n_split in enumerate(n_splits, start=1):
                split_players_id = players_id[cur_index:cur_index + n_split] # select group members
                new_structure.append(split_players_id) # ???? Isn't it the same as players_id after all?
                new_ids = list(range(1, len(split_players_id)+1)) # new ID within a group, from 1 to group size
                for j, new_id in enumerate(new_ids):
                    self.session.vars['new_id_to_ori_id'][f'{group_id}-{new_id}'] = split_players_id[j]
                split_rounds_tournament = group.game_scheduler(new_ids, shuffle=False)
                self.session.vars['all_rounds_tournament'][group_id] = split_rounds_tournament # Recall that this is a dictionary
                cur_index += n_split
            self.set_group_matrix(new_structure) # see otree document for formatting
            print(self.session.vars['all_rounds_tournament'])

        else:
            self.group_like_round(1) # fix group composition throughout

class Group(BaseGroup):
    game_over = models.BooleanField(initial=False)

    def confirm_game_over(self):
        num_players = len(self.get_players()) # group size
        if self.round_number == Constants.num_trials * (num_players - 1):
            self.set_game_over(game_over=True)

    def set_game_over(self, game_over):
        self.game_over = game_over

    def game_scheduler(self, players_id, shuffle=False):
        # build players' ids
        players_id = np.array(players_id)
        num_of_players = len(players_id)
        if shuffle:
            np.random.shuffle(players_id)
        if num_of_players % 2 != 0:
            # add a virtual player so that the number of players is a multiple of 2
            players_id = np.append(players_id, -1)
            num_of_players += 1
        players_id = players_id.reshape(-1, 2)  # -1 automatical calculate the number of rows, 2 means that we always
        # want to 2 columns
        anchor_id = players_id[0, 0]  # upper left position in the n/2 by 2 matrix
        circle_ids = np.append(players_id[1:, 0], list(reversed(players_id[:, 1])))
        id2cirIdx = dict(zip(circle_ids, list(range(len(circle_ids)))))
        cir_real_indices = ([(row, 0) for row in range(1, len(players_id[1:, 0]) + 1)] +
                            [(row, 1) for row in
                             range(len(players_id[:, 1]) - 1, -1, -1)])  # "+" is to combine vectors into a list
        cirIdx2realIdx = dict(zip(id2cirIdx.values(), cir_real_indices))

        # use two dicts to update each round scheduled players' ids
        rounds_scheduled_ids = list()
        for round in range(1, len(circle_ids) + 1):
            sheduled_ids = np.zeros(players_id.shape)
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
        split_rounds_tournament = self.session.vars['all_rounds_tournament'][self.id_in_subsession] # id_in_subsession is actually group ID
        num_players = len(self.get_players())
        current_round_match = split_rounds_tournament[current_round_num % (num_players - 1) - 1]
        for k in current_round_match:
            i, j = k
            player_i = self.get_player_by_id(i)
            player_j = self.get_player_by_id(j)
            player_i.set_opponent(j)
            player_j.set_opponent(i)

    def competition_calculation(self):
        current_round_num = self.round_number
        split_rounds_tournament = self.session.vars['all_rounds_tournament'][self.id_in_subsession]
        num_players = len(self.get_players())
        current_round_match = split_rounds_tournament[current_round_num % (num_players - 1) - 1]
        for k in current_round_match:
            i, j = k
            player_i = self.get_player_by_id(i)
            player_j = self.get_player_by_id(j)
            performance_i = player_i.efforts + player_i.participant.vars['talents']
            performance_j = player_j.efforts + player_j.participant.vars['talents']
            if performance_i > performance_j:
                player_i.participant.vars['accounts'] = Constants.REWARD + (Constants.EFFORTS-player_i.efforts)
                player_j.participant.vars['accounts'] = (Constants.EFFORTS-player_j.efforts)
                player_i.participant.vars['records'].append(1)
                player_i.round_results = 1
                player_j.participant.vars['records'].append(0)
                player_j.round_results = 0
            elif performance_i == performance_j:
                player_i.participant.vars['accounts'] = Constants.REWARD/2 + (Constants.EFFORTS-player_i.efforts)
                player_j.participant.vars['accounts'] = Constants.REWARD/2 + (Constants.EFFORTS-player_j.efforts)
                player_i.participant.vars['records'].append(0.5)
                player_i.round_results = 0.5
                player_j.participant.vars['records'].append(0.5)
                player_j.round_results = 0.5
            else:
                player_i.participant.vars['accounts'] = (Constants.EFFORTS-player_i.efforts)
                player_j.participant.vars['accounts'] = Constants.REWARD + (Constants.EFFORTS-player_j.efforts)
                player_i.participant.vars['records'].append(0)
                player_i.round_results = 0
                player_j.participant.vars['records'].append(1)
                player_j.round_results = 1
            player_i.payoff = player_i.participant.vars['accounts']
            player_j.payoff = player_j.participant.vars['accounts']

    def ranking_calculation(self):
        # if self.round_number % (self.session.num_participants - 1) == 0:
        players_records = []
        for player in self.get_players():
            player_i = self.get_player_by_id(player.id_in_group)
            players_records.append(np.mean(player_i.participant.vars['records']))

        sort_raw = sorted(range(len(players_records)), key=lambda k: players_records[k])
        for i in sort_raw:
            player_i = self.get_player_by_id(sort_raw[i] + 1)
            player_i.participant.vars['ranking'] = i

    def check_revealtion_decision(self):
        for p in self.get_players():
            p.process_reveal_ability()
            p.process_reveal_victory()
            p.calculate_reveal_decisions()


class Player(BasePlayer):
    talents = models.IntegerField()
    opponent = models.IntegerField()
    records = models.FloatField()
    round_results = models.FloatField()

    efforts = models.IntegerField(choices=range(0, 11), widget=widgets.Slider(attrs={'max': '10'}))

    ability_revelation = models.BooleanField(widget=widgets.RadioSelect,
                                             choices=[[False,'不要'],[True,'要'],
                                                      ])

    victory_revelation = models.BooleanField(widget=widgets.RadioSelect,
                                             choices=[[False, '不要'], [True, '要'],
                                                      ])

    def get_id(self):
        return self.participant.vars['id']

    def set_opponent(self, rival):
        self.opponent = rival

    def get_opponent(self):
        return self.opponent

    def get_ori_opponent_id(self):
        new_id = self.get_opponent()
        return self.session.vars['new_id_to_ori_id'][f'{self.group.id_in_subsession}-{new_id}']

    def get_opponent_ranking(self):
        return self.group.get_player_by_id(self.opponent).participant.vars['ranking']

    def get_personal_records(self):
        return np.round(np.mean(self.participant.vars['records']), 2)

    def get_personal_ranking(self):
        return self.participant.vars['ranking']

    def get_personal_talents(self):
        return self.participant.vars['talents']

    def get_players_prev_fields(self, field_str):
        prev_fields = list()
        # for player in self.group.get_players():  # p1, .... ,p10
        for prevSelf in self.in_previous_rounds():
            prev_fields.append(getattr(prevSelf, field_str))
        return prev_fields

    def print_round_result(self):
        if self.round_results == 1:
            outcome = "勝"
        elif self.round_results == 0.5:
            outcome = "平手"
        else:
            outcome = "敗"
        return outcome

    def print_round_payoff(self):
        if self.round_results == 1:
            payout = Constants.REWARD
        elif self.round_results == 0.5:
            payout = Constants.REWARD*0.5
        else:
            payout = 0
        return payout

    def process_reveal_ability(self):
        if self.ability_revelation :
            my_opponent = self.group.get_player_by_id(self.opponent)
            answer = my_opponent.participant.vars['talents'] # ???? why not start with self here?
            efforts_allowed = 10

        else:
            answer = "不透露"
            efforts_allowed = 0
        return answer, efforts_allowed

    def process_reveal_victory(self):
        if self.victory_revelation :
            my_opponent = self.group.get_player_by_id(self.opponent)
            answer = my_opponent.get_personal_records()
        else:
            answer = "不透露"
        return answer

    def calculate_reveal_decisions(self):
        if self.round_number > 1:
            past_egos = self.in_previous_rounds()
            frequency_ability_reveal = []
            frequency_records_reveal = []
            for p in past_egos:
                frequency_ability_reveal.append(p.ability_revelation)
                frequency_records_reveal.append(p.ability_revelation)
            frequency_ability_reveal = sum(frequency_ability_reveal)
            frequency_records_reveal = sum(frequency_records_reveal)

        else:
            frequency_ability_reveal = "暫無紀錄"
            frequency_records_reveal = "暫無紀錄"
        return frequency_ability_reveal, frequency_records_reveal


