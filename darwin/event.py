import random


class Event:

    def __init__(self, name, description, pillar):

        self.name = name
        self.description = description
        self.pillar = pillar

    def show(self):

        print()
        print("=" * 70)
        print(f"EVENTO: {self.name}")
        print("=" * 70)

        print(self.description)

        print()
        print(f"Pilar principal: {self.pillar}")


class EventGenerator:

    def __init__(self):

        self.events = [

            Event(
                "Surpresa de aniversário",
                "Um grupo de amigos prepara uma surpresa para uma pessoa.",
                "Respeito"
            ),

            Event(
                "Acidente de trânsito",
                "Uma pessoa se envolve em um acidente e precisa decidir como agir.",
                "Responsabilidade"
            ),

            Event(
                "Lixo na praça",
                "Um indivíduo encontra lixo espalhado em uma praça pública.",
                "Zelo"
            ),

            Event(
                "Conflito na comunidade",
                "Duas pessoas discordam sobre uma decisão que afeta a comunidade.",
                "Justiça"
            ),

            Event(
                "Informação duvidosa",
                "Uma pessoa recebe uma informação que pode ser falsa.",
                "Sinceridade"
            ),

            Event(
                "Problema coletivo",
                "A comunidade precisa trabalhar junta para resolver um problema.",
                "Cidadania"
            )
        ]

    def random_event(self):

        return random.choice(self.events)