from darwin.individual import Individual
from darwin.event import EventGenerator
from darwin.social import Social


class Population:

    def __init__(self, size):

        self.individuals = [
            Individual(i)
            for i in range(size)
        ]

        # Sistema de eventos
        self.event_generator = EventGenerator()

        # Sistema de interações sociais
        self.social = Social(self.individuals)

        # Histórico da população
        self.history = []

    # ==========================================================
    # UTILITÁRIOS
    # ==========================================================

    def calculate_average(self, attribute):

        if not self.individuals:
            return 0

        total = sum(
            getattr(individual, attribute)
            for individual in self.individuals
        )

        return total / len(self.individuals)

    # ==========================================================
    # HISTÓRICO
    # ==========================================================

    def save_history(self, day):

        self.history.append({
            "day": day,

            "respeito": self.calculate_average(
                "respeito"
            ),

            "cidadania": self.calculate_average(
                "cidadania"
            ),

            "responsabilidade": self.calculate_average(
                "responsabilidade"
            ),

            "zelo": self.calculate_average(
                "zelo"
            ),

            "justica": self.calculate_average(
                "justica"
            ),

            "sinceridade": self.calculate_average(
                "sinceridade"
            ),

            "wellbeing": self.calculate_average(
                "wellbeing"
            ),

            "social_score": sum(
                individual.social_score()
                for individual in self.individuals
            ) / len(self.individuals)
        })

    # ==========================================================
    # UM DIA
    # ==========================================================

    def simulate_day(self, day):

        # ------------------------------------------------------
        # 1. EVENTO EXTERNO
        # ------------------------------------------------------

        event = self.event_generator.random_event()

        print(
            f"\nDia {day}: "
            f"{event.name}"
        )

        # Cada indivíduo percebe o mesmo evento
        for individual in self.individuals:

            self.social.perform_event(
                individual,
                event,
                day
            )

        # ------------------------------------------------------
        # 2. INTERAÇÕES ENTRE INDIVÍDUOS
        # ------------------------------------------------------

        self.social.simulate_interactions(
            day
        )

        # ------------------------------------------------------
        # 3. SALVA O ESTADO DA SOCIEDADE
        # ------------------------------------------------------

        self.save_history(day)

    # ==========================================================
    # SIMULAÇÃO COMPLETA
    # ==========================================================

    def simulate(self, days):

        for day in range(1, days + 1):

            self.simulate_day(day)

    # ==========================================================
    # RANKING
    # ==========================================================

    def best_individuals(self, amount=10):

        return sorted(
            self.individuals,
            key=lambda individual: individual.social_score(),
            reverse=True
        )[:amount]

    # ==========================================================
    # STATUS
    # ==========================================================

    def show_status(self):

        print("\n")
        print("=" * 70)
        print("📊 ESTADO FINAL DA SOCIEDADE")
        print("=" * 70)

        print(
            f"\nPopulação: "
            f"{len(self.individuals)}"
        )

        print(
            f"Interações realizadas: "
            f"{self.social.total_interactions}"
        )

        print("\nMédia dos pilares:")

        print(
            f"Respeito:          "
            f"{self.calculate_average('respeito'):.2f}"
        )

        print(
            f"Cidadania:         "
            f"{self.calculate_average('cidadania'):.2f}"
        )

        print(
            f"Responsabilidade:  "
            f"{self.calculate_average('responsabilidade'):.2f}"
        )

        print(
            f"Zelo:              "
            f"{self.calculate_average('zelo'):.2f}"
        )

        print(
            f"Justiça:           "
            f"{self.calculate_average('justica'):.2f}"
        )

        print(
            f"Sinceridade:       "
            f"{self.calculate_average('sinceridade'):.2f}"
        )

        print(
            f"\nPontuação social média: "
            f"{sum(i.social_score() for i in self.individuals) / len(self.individuals):.2f}"
        )

        print(
            f"Bem-estar médio: "
            f"{self.calculate_average('wellbeing'):.2f}"
        )

        # ------------------------------------------------------
        # TOP 5
        # ------------------------------------------------------

        print("\n" + "-" * 70)
        print("🏆 TOP 5")
        print("-" * 70)

        for position, individual in enumerate(
            self.best_individuals(5),
            start=1
        ):

            print(
                f"{position}º "
                f"{individual.name:<15} "
                f"Social: "
                f"{individual.social_score():.2f}"
            )
