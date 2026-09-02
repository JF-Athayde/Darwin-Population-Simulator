from random import uniform, randint


class Individual:

    def __init__(self, idx, bounds=(0, 10)):
        self.id = idx
        self.name = self.build_name()

        # Características antigas
        self.strength = uniform(*bounds)
        self.speed = uniform(*bounds)
        self.luck = uniform(*bounds)
        self.smart = uniform(*bounds)
        self.dexterity = uniform(*bounds)
        self.wisdom = uniform(*bounds)
        self.charisma = uniform(*bounds)
        self.beauty = uniform(*bounds)

        # Pilares sociais
        self.respeito = uniform(*bounds)
        self.cidadania = uniform(*bounds)
        self.responsabilidade = uniform(*bounds)
        self.zelo = uniform(*bounds)
        self.justica = uniform(*bounds)
        self.sinceridade = uniform(*bounds)

        # Estado social
        self.trust = 5.0
        self.influence = 5.0
        self.wellbeing = 100.0

        # Estatísticas de comportamento
        self.people_helped = 0
        self.conflicts_resolved = 0
        self.conflicts_created = 0

        self.responsibilities_taken = 0
        self.citizenship_actions = 0
        self.care_actions = 0

        # Quantidade de cada ação realizada
        self.action_counts = {}

        # Histórico completo
        self.history = []

        # Guarda os valores iniciais para comparar evolução
        self.initial_pillars = self.get_pillars().copy()

        self.perception = ""
        self.last_action = ""

    def build_name(self):
        names = [
            "Ana", "João", "Maria", "Pedro",
            "Lucas", "Julia", "Gabriel", "Laura",
            "Miguel", "Sofia", "Arthur", "Beatriz",
            "Rafael", "Helena", "Davi", "Alice"
        ]

        return names[self.id % len(names)] + f"_{self.id}"

    def clamp(self, value, minimum=0, maximum=10):
        return max(minimum, min(maximum, value))

    def get_pillars(self):
        return {
            "Respeito": self.respeito,
            "Cidadania": self.cidadania,
            "Responsabilidade": self.responsabilidade,
            "Zelo": self.zelo,
            "Justiça": self.justica,
            "Sinceridade": self.sinceridade
        }

    def social_score(self):
        pillars = self.get_pillars()

        return sum(pillars.values()) / len(pillars)

    def register_action(
        self,
        day,
        event,
        perception,
        action,
        pillar,
        score_before,
        score_after
    ):
        # Conta quantas vezes a ação apareceu
        if action not in self.action_counts:
            self.action_counts[action] = 0

        self.action_counts[action] += 1

        # Salva tudo que aconteceu
        self.history.append({
            "day": day,
            "event": event.name,
            "description": event.description,
            "perception": perception,
            "action": action,
            "pillar": pillar,
            "score_before": score_before,
            "score_after": score_after,
            "delta": score_after - score_before
        })

    def show(self):
        print(
            f"{self.name} | "
            f"Social: {self.social_score():.2f} | "
            f"Bem-estar: {self.wellbeing:.2f}"
        )

    def show_full_report(self):
        print("\n")
        print("=" * 70)
        print("🏆 INDIVÍDUO COM MAIOR PONTUAÇÃO SOCIAL")
        print("=" * 70)

        print(f"\nNome: {self.name}")
        print(f"ID: {self.id}")
        print(f"Pontuação social: {self.social_score():.2f}")

        print("\n" + "-" * 70)
        print("📊 EVOLUÇÃO DOS PILARES")
        print("-" * 70)

        pillars = self.get_pillars()

        for pillar, value in pillars.items():
            initial = self.initial_pillars[pillar]
            evolution = value - initial

            print(
                f"{pillar:<18} "
                f"{initial:5.2f} → {value:5.2f} "
                f"({evolution:+.2f})"
            )

        print("\n" + "-" * 70)
        print("🤝 CONTRIBUIÇÕES SOCIAIS")
        print("-" * 70)

        print(f"Pessoas ajudadas:          {self.people_helped}")
        print(f"Conflitos resolvidos:      {self.conflicts_resolved}")
        print(f"Conflitos criados:         {self.conflicts_created}")
        print(f"Responsabilidades:         {self.responsibilities_taken}")
        print(f"Ações de cidadania:        {self.citizenship_actions}")
        print(f"Ações de zelo:             {self.care_actions}")

        print("\n" + "-" * 70)
        print("🧠 AÇÕES MAIS REALIZADAS")
        print("-" * 70)

        if self.action_counts:

            actions = sorted(
                self.action_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )

            for action, amount in actions:
                print(f"{action:<35} {amount} vezes")

        print("\n" + "-" * 70)
        print("📜 HISTÓRICO DE DECISÕES")
        print("-" * 70)

        if not self.history:
            print("Nenhuma ação registrada.")

        else:
            # Mostra até 15 acontecimentos
            for item in self.history[:15]:

                print(
                    f"\nDia {item['day']} | "
                    f"{item['event']}"
                )

                print(
                    f"  Percepção: {item['perception']}"
                )

                print(
                    f"  Decisão: {item['action']}"
                )

                print(
                    f"  Pilar afetado: {item['pillar']}"
                )

                print(
                    f"  Pontuação: "
                    f"{item['score_before']:.2f} → "
                    f"{item['score_after']:.2f}"
                )

        if len(self.history) > 15:

            print(
                f"\n... e mais "
                f"{len(self.history) - 15} acontecimentos."
            )

        print("\n" + "=" * 70)
