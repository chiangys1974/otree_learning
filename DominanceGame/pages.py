from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class Instruction(Page):
    form_model = 'player'

    def is_displayed(self):
        return self.round_number == 1


class MatchWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.match_players()


class GamePage(Page):
    timeout_seconds = 90
    form_model = 'player'
    form_fields = ['efforts']

    def vars_for_template(self):
        return {
            'cur_id': self.player.get_id(),
            'rival': self.player.get_opponent(),
            'your_talent': self.player.get_personal_talents(),
        }


class ResultsWaitPage(WaitPage):

    def after_all_players_arrive(self):
        self.group.competition_calculation()
        self.group.ranking_calculation()


class Results(Page):
    def vars_for_template(self):
        return {
            'winning_rate': self.player.get_personal_records(),
            'ranking_record': self.player.get_personal_ranking(),
            'ranking_or_not': self.round_number % (self.session.num_participants - 1) == 0
        }


class FinalPage(Page):

    def is_displayed(self):
        self.group.confirm_game_over()
        return self.group.game_over

page_sequence = [
    Instruction,
    MatchWaitPage,
    GamePage,
    ResultsWaitPage,
    Results,
    FinalPage,
]
