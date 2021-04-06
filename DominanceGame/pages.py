from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Instruction(Page):

    timeout_seconds = 300
    form_model = 'player'

    def is_displayed(self):
        return self.round_number == 1


class Instruction2(Page):

    timeout_seconds = 150
    form_model = 'player'

    def is_displayed(self):
        return self.round_number == 1


class MatchWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.match_players()


class InformationPage(Page):

    timeout_seconds = 60
    form_model = 'player'

    def get_form_fields(self):
        if self.round_number > 1:
            return ['victory_revelation',
                    'ability_revelation']
        else:
            return ['ability_revelation']


    def vars_for_template(self):
        return{
            'frequency_ability_reveal': self.player.calculate_reveal_decisions()[0],
            'frequency_victory_reveal': self.player.calculate_reveal_decisions()[1],
            'past_round_number': self.round_number-1,
            'rival': self.player.get_ori_opponent_id(),
        }

class InfoWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.check_revealtion_decision()


class GamePage(Page):
    timeout_seconds = 120
    form_model = 'player'
    form_fields = ['efforts']

    def vars_for_template(self):
        # call a function and define a tuple. then use index to call out
        return {
            'cur_id': self.player.get_id(),
            'rival': self.player.get_ori_opponent_id(),
            'your_talent': self.player.get_personal_talents(),
            'your_record': self.player.get_personal_records(),
            'opponent_rank': self.player.get_opponent_ranking(),
            'reveal_ability': self.player.process_reveal_ability()[0],
            'reveal_victory': self.player.process_reveal_victory(),
            'rival_efforts_allowed': self.player.process_reveal_ability()[1]
        }


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.competition_calculation()
        self.group.ranking_calculation()


class Results(Page):

    timeout_seconds = 30

    def vars_for_template(self):
        return {
            'winning_rate': self.player.get_personal_records(),
            'ranking_record': self.player.get_personal_ranking(),
            'ranking_or_not': self.round_number % (self.session.num_participants - 1) == 0,
            'round_result': self.player.print_round_result(),
            'round_payout': self.player.print_round_payoff()
        }


class FinalPage(Page):

    def is_displayed(self):
        self.group.confirm_game_over()
        return self.group.game_over

    def vars_for_template(self):

        part_fee = (self.participant.payoff / self.round_number) * self.session.config['real_world_currency_per_point'] + self.session.config['participation_fee']
        return {
            'payoff_plus_participation_fee': '{:.2f}'.format(part_fee),
        }


page_sequence = [
    Instruction,
    Instruction2,
    MatchWaitPage,
    InformationPage,
    InfoWaitPage,
    GamePage,
    ResultsWaitPage,
    Results,
    FinalPage,
]
