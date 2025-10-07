from requests import Response

from .lib import Base


class Polls(Base):

    def create(
            self,
            answers: list[str],
            question: str,
            room_id: str,
            multiple_choice: bool = False,
            public_voters: bool = True,
    ) -> Response:
        """Создание голосования.

        :param answers: варианты ответов
        :param question: вопросы
        :param room_id: uid комнаты
        :param multiple_choice: можно ли выбирать больше 1 варианта
        :param public_voters: можно ли просматривать кто голосовал
        :param message_id: uid сообщения которое будет создано

        :return: requests.Response
        """
        return self._make_request(
            endpoint='polls.create',
            payload={
                'answers': answers,
                'question': question,
                'roomId': room_id,
                'multipleChoice': multiple_choice,
                'publicVoters': public_voters,
            })

    def vote(self, msg_id: str, answer_ids: list[str]) -> Response:
        """Проголосовать.

        :param msg_id: uid голосования
        :param answer_ids: uid вариантов ответа

        :return: requests.Response
        """
        return self._make_request(
            endpoint='polls.vote',
            payload={
                'msgId': msg_id,
                'options': answer_ids,
            })

    def poll_results(self, poll_id: str):
        """Результаты голосования.

        :param poll_id: uid голосования

        :return: requests.Response
        """
        return self._make_request(
            endpoint='polls.results',
            params={
                'msgId': poll_id,
            },
            method='get',
        )

    def poll_votes(self, poll_id: str):
        """Список голосов.

        :param poll_id: uid голосования

        :return: requests.Response
        """
        return self._make_request(
            endpoint='polls.votes',
            params={
                'msgId': poll_id,
            },
            method='get',
        )

    def retract_vote(self, poll_id: str):
        """Отозвать голос за вариант голосования.

        :param poll_id: uid голосования

        :return: requests.Response
        """
        return self._make_request(
            endpoint='polls.retractVote',
            payload={
                'msgId': poll_id,
            },
        )
