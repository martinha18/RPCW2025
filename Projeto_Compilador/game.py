import threading

class Game:
    def __init__(self, client, room_id, questions, adm_id, cleanup):
        self.client = client
        self.room_id = room_id
        self.questions = questions
        self.adm_id = adm_id
        self.players = {}
        self.current_question = -1
        self.game_started = False
        self.stage_open = False
        self.answers_received = set()
        self.timer = None
        self.cleanup = cleanup

    def player_connect(self, player_id, username):
        if self.game_started:
            self.client.emit('game_already_started', {'error': 'Game has already started'}, to=player_id)
        else:
            self.players[player_id] = {'score': 0, 'username': username}

            players = []
            for id, player in self.players.items():
                players.append({'player_id': id, 'username': player['username']})
            self.client.emit('player_joined', players, to=self.room_id)

    def player_disconnect(self, player_id):
        if player_id in self.players:
            del self.players[player_id]
            self.client.emit('player_left', {'player_id': player_id}, to=self.room_id)

            if player_id in self.answers_received:
                self.answers_received.remove(player_id)

            if len(self.players) == 0:
                self.game_terminated()

        if player_id == self.adm_id:
            self.game_terminated()

    def adm_start(self, adm_id):
        if adm_id == self.adm_id and not self.game_started:
            self.game_started = True
            self.adm_next(adm_id)

    def adm_next(self, adm_id):
        if adm_id == self.adm_id and self.current_question + 1 < len(self.questions) and not self.stage_open:
            self.current_question += 1
            self.answers_received.clear()
            self.stage_open = True
            self.client.emit('new_question', self.questions[self.current_question], to=self.room_id)

            self.timer = threading.Timer(30, self.stage_terminated)
            self.timer.start()

    def player_answer(self, player_id, answer):
        if not self.game_started or not self.stage_open:
            return  

        if player_id in self.players and player_id not in self.answers_received:
            correct_answer = self.questions[self.current_question]['answer']
            self.answers_received.add(player_id)

            if answer == correct_answer:
                self.players[player_id]['score'] += 1

            self.client.emit('player_answered', {'player_id': player_id}, to=self.room_id)

            if len(self.answers_received) == len(self.players):
                self.stage_terminated()

    def stage_terminated(self):
        if self.timer:
            self.timer.cancel()

        self.stage_open = False
        self.client.emit('game_stage_terminated', to=self.room_id)

        if self.current_question + 1 >= len(self.questions):
            self.game_terminated()

    def game_terminated(self):
        self.client.emit('game_terminated', self.players, to=self.room_id)
        self.client.close_room(self.room_id)
        self.cleanup(self.room_id)
