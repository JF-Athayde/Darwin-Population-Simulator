import matplotlib.pyplot as plt


class Visualization:

    def __init__(self, population):
        self.population = population

    # ==========================================================
    # AUXILIAR
    # ==========================================================

    def get_history_data(self, key):
        return [
            entry[key]
            for entry in self.population.history
        ]

    def get_days(self):
        return [
            entry["day"]
            for entry in self.population.history
        ]

    # ==========================================================
    # PILARES
    # ==========================================================

    def plot_pillars(self):

        days = self.get_days()

        pillars = [
            "respeito",
            "cidadania",
            "responsabilidade",
            "zelo",
            "justica",
            "sinceridade"
        ]

        names = {
            "respeito": "Respeito",
            "cidadania": "Cidadania",
            "responsabilidade": "Responsabilidade",
            "zelo": "Zelo",
            "justica": "Justiça",
            "sinceridade": "Sinceridade"
        }

        plt.figure(figsize=(12, 6))

        for pillar in pillars:
            values = self.get_history_data(pillar)
            plt.plot(
                days,
                values,
                label=names[pillar]
            )

        plt.title(
            "Evolução dos Pilares da Sociedade"
        )

        plt.xlabel("Dia")
        plt.ylabel("Pontuação")

        plt.ylim(0, 10)

        plt.grid(True)
        plt.legend()

        plt.tight_layout()
        plt.show()

    # ==========================================================
    # BEM-ESTAR
    # ==========================================================

    def plot_wellbeing(self):

        days = self.get_days()
        values = self.get_history_data(
            "wellbeing"
        )

        plt.figure(figsize=(12, 5))

        plt.plot(
            days,
            values,
            linewidth=2
        )

        plt.title(
            "Evolução do Bem-estar Médio"
        )

        plt.xlabel("Dia")
        plt.ylabel("Bem-estar")

        plt.grid(True)
        plt.tight_layout()

        plt.show()

    