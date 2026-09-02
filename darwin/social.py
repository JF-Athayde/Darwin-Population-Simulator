import random


class Social:

    def __init__(self, individuals):

        self.individuals = individuals
        self.interactions = []
        self.total_interactions = 0

        # ======================================================
        # MAPA DOS PILARES
        # ======================================================

        self.pillar_map = {
            "respeito": "respeito",
            "cidadania": "cidadania",
            "responsabilidade": "responsabilidade",
            "zelo": "zelo",
            "justiça": "justica",
            "justica": "justica",
            "sinceridade": "sinceridade"
        }

    # ==========================================================
    # UTILIDADES
    # ==========================================================

    def get_pillar_attribute(self, pillar):

        """
        Converte o nome do pilar para o atributo
        correspondente dentro do Individual.
        """

        pillar = str(pillar).lower().strip()

        if pillar not in self.pillar_map:

            raise ValueError(
                f"Pilar desconhecido: {pillar}"
            )

        return self.pillar_map[pillar]

    # ==========================================================

    def clamp(
        self,
        value,
        minimum=0,
        maximum=100
    ):

        """
        Mantém valores dentro de 0 e 100.
        """

        return max(
            minimum,
            min(maximum, value)
        )

    # ==========================================================

    def get_attribute(
        self,
        individual,
        attribute,
        default=50
    ):

        """
        Obtém um atributo de forma segura.
        """

        return getattr(
            individual,
            attribute,
            default
        )

    # ==========================================================
    # PERCEPÇÃO DO EVENTO
    # ==========================================================

    def perceive_event(
        self,
        individual,
        event
    ):

        """
        Cada indivíduo percebe o mesmo evento
        de uma maneira diferente.

        A percepção depende de:

        - Pilar relacionado ao evento
        - Inteligência
        - Sabedoria
        - Pequena aleatoriedade
        """

        pillar = str(
            event.pillar
        ).lower().strip()

        attribute = self.get_pillar_attribute(
            pillar
        )

        # ------------------------------------------------------
        # ATRIBUTO DO PILAR
        # ------------------------------------------------------

        pillar_value = self.get_attribute(
            individual,
            attribute,
            50
        )

        # ------------------------------------------------------
        # INTELIGÊNCIA
        # ------------------------------------------------------

        smart = self.get_attribute(
            individual,
            "smart",
            50
        )

        # ------------------------------------------------------
        # SABEDORIA
        # ------------------------------------------------------

        wisdom = self.get_attribute(
            individual,
            "wisdom",
            50
        )

        # ------------------------------------------------------
        # CAPACIDADE COGNITIVA
        # ------------------------------------------------------

        cognitive_score = (
            smart * 0.5
            + wisdom * 0.5
        )

        # ------------------------------------------------------
        # PERCEPÇÃO BASE
        # ------------------------------------------------------

        perception_score = (
            pillar_value * 0.60
            + cognitive_score * 0.40
        )

        # ------------------------------------------------------
        # RUÍDO
        # ------------------------------------------------------

        noise = random.uniform(
            -8,
            8
        )

        perception_score += noise

        perception_score = self.clamp(
            perception_score
        )

        # ======================================================
        # DESCRIÇÃO
        # ======================================================

        if perception_score >= 80:

            perception = (
                "Percebeu o evento como uma situação "
                "muito importante e que exige uma atitude correta."
            )

        elif perception_score >= 65:

            perception = (
                "Percebeu o evento como uma situação "
                "importante que merece atenção."
            )

        elif perception_score >= 50:

            perception = (
                "Percebeu o evento como uma situação "
                "relevante, mas controlável."
            )

        elif perception_score >= 35:

            perception = (
                "Percebeu o evento como uma situação comum "
                "que pode exigir alguma atenção."
            )

        elif perception_score >= 20:

            perception = (
                "Percebeu pouca importância no evento."
            )

        else:

            perception = (
                "Quase não percebeu a importância do evento."
            )

        return {
            "score": perception_score,
            "description": perception
        }

    # ==========================================================
    # ESCOLHA DA AÇÃO
    # ==========================================================

    def choose_event_action(
        self,
        individual,
        event,
        perception
    ):

        """
        Decide o comportamento do indivíduo.

        IMPORTANTE:

        O sistema não força indivíduos com baixo atributo
        a sempre agirem incorretamente.

        Existe sempre alguma chance de:

        - agir corretamente
        - ajudar
        - ignorar
        - agir incorretamente
        """

        pillar = str(
            event.pillar
        ).lower().strip()

        attribute = self.get_pillar_attribute(
            pillar
        )

        # ------------------------------------------------------
        # VALORES DO INDIVÍDUO
        # ------------------------------------------------------

        pillar_value = self.get_attribute(
            individual,
            attribute,
            50
        )

        intelligence = self.get_attribute(
            individual,
            "smart",
            50
        )

        wisdom = self.get_attribute(
            individual,
            "wisdom",
            50
        )

        perception_score = perception["score"]

        # ======================================================
        # CAPACIDADE SOCIAL
        # ======================================================

        social_ability = (
            pillar_value * 0.40
            + intelligence * 0.30
            + wisdom * 0.30
        )

        # ======================================================
        # SCORE DE DECISÃO
        # ======================================================

        decision_score = (
            social_ability * 0.60
            + perception_score * 0.40
        )

        decision_score = self.clamp(
            decision_score
        )

        # ======================================================
        # PROBABILIDADES
        # ======================================================

        # Valores base.
        correct_probability = 15
        help_probability = 10
        ignore_probability = 35
        incorrect_probability = 40

        # ------------------------------------------------------
        # SCORE ALTO
        # ------------------------------------------------------

        if decision_score >= 75:

            correct_probability = 50
            help_probability = 32
            ignore_probability = 15
            incorrect_probability = 3

        # ------------------------------------------------------
        # SCORE BOM
        # ------------------------------------------------------

        elif decision_score >= 65:

            correct_probability = 42
            help_probability = 30
            ignore_probability = 22
            incorrect_probability = 6

        # ------------------------------------------------------
        # SCORE MÉDIO
        # ------------------------------------------------------

        elif decision_score >= 55:

            correct_probability = 35
            help_probability = 27
            ignore_probability = 30
            incorrect_probability = 8

        # ------------------------------------------------------
        # SCORE MEDIANO
        # ------------------------------------------------------

        elif decision_score >= 45:

            correct_probability = 28
            help_probability = 24
            ignore_probability = 36
            incorrect_probability = 12

        # ------------------------------------------------------
        # SCORE BAIXO
        # ------------------------------------------------------

        elif decision_score >= 35:

            correct_probability = 22
            help_probability = 18
            ignore_probability = 40
            incorrect_probability = 20

        # ------------------------------------------------------
        # SCORE MUITO BAIXO
        # ------------------------------------------------------

        else:

            correct_probability = 12
            help_probability = 12
            ignore_probability = 41
            incorrect_probability = 35

        # ======================================================
        # ESCOLHA
        # ======================================================

        chance = random.uniform(
            0,
            100
        )

        if chance < correct_probability:

            return "agir_corretamente"

        elif chance < (
            correct_probability
            + help_probability
        ):

            return "ajudar"

        elif chance < (
            correct_probability
            + help_probability
            + ignore_probability
        ):

            return "ignorar"

        return "agir_incorretamente"

    # ==========================================================
    # CONSEQUÊNCIA DA AÇÃO
    # ==========================================================

    def apply_event_action(
        self,
        individual,
        event,
        action
    ):

        """
        Aplica a consequência da ação.

        Os valores foram reduzidos para evitar
        o colapso rápido dos pilares.
        """

        pillar = str(
            event.pillar
        ).lower().strip()

        attribute = self.get_pillar_attribute(
            pillar
        )

        current_value = self.get_attribute(
            individual,
            attribute,
            50
        )

        # ======================================================
        # AGIR CORRETAMENTE
        # ======================================================

        if action == "agir_corretamente":

            # Ganho moderado
            setattr(
                individual,
                attribute,
                self.clamp(
                    current_value + 0.8
                )
            )

            # Confiança
            if hasattr(
                individual,
                "trust"
            ):

                individual.trust = self.clamp(
                    individual.trust + 0.4
                )

            # Influência
            if hasattr(
                individual,
                "influence"
            ):

                individual.influence = self.clamp(
                    individual.influence + 0.2
                )

            # Bem-estar
            if hasattr(
                individual,
                "wellbeing"
            ):

                individual.wellbeing = self.clamp(
                    individual.wellbeing + 0.2
                )

        # ======================================================
        # AJUDAR
        # ======================================================

        elif action == "ajudar":

            # Ajudar possui um ganho um pouco maior
            setattr(
                individual,
                attribute,
                self.clamp(
                    current_value + 1.2
                )
            )

            # Confiança
            if hasattr(
                individual,
                "trust"
            ):

                individual.trust = self.clamp(
                    individual.trust + 0.8
                )

            # Influência
            if hasattr(
                individual,
                "influence"
            ):

                individual.influence = self.clamp(
                    individual.influence + 0.6
                )

            # Bem-estar
            if hasattr(
                individual,
                "wellbeing"
            ):

                individual.wellbeing = self.clamp(
                    individual.wellbeing + 0.5
                )

            # Pessoas ajudadas
            if hasattr(
                individual,
                "people_helped"
            ):

                individual.people_helped += 1

        # ======================================================
        # IGNORAR
        # ======================================================

        elif action == "ignorar":

            # Pequena penalização
            setattr(
                individual,
                attribute,
                self.clamp(
                    current_value - 0.05
                )
            )

            if hasattr(
                individual,
                "trust"
            ):

                individual.trust = self.clamp(
                    individual.trust - 0.03
                )

        # ======================================================
        # AGIR INCORRETAMENTE
        # ======================================================

        elif action == "agir_incorretamente":

            # Penalização relevante,
            # porém não destrutiva.
            setattr(
                individual,
                attribute,
                self.clamp(
                    current_value - 0.8
                )
            )

            if hasattr(
                individual,
                "trust"
            ):

                individual.trust = self.clamp(
                    individual.trust - 0.5
                )

            if hasattr(
                individual,
                "influence"
            ):

                individual.influence = self.clamp(
                    individual.influence - 0.3
                )

            if hasattr(
                individual,
                "wellbeing"
            ):

                individual.wellbeing = self.clamp(
                    individual.wellbeing - 0.3
                )

    # ==========================================================
    # EVENTO INDIVIDUAL
    # ==========================================================

    def perform_event(
        self,
        individual,
        event,
        day
    ):

        """
        Executa:

        EVENTO
           ↓
        PERCEPÇÃO
           ↓
        DECISÃO
           ↓
        AÇÃO
           ↓
        CONSEQUÊNCIA
           ↓
        HISTÓRICO
        """

        # ======================================================
        # PILAR
        # ======================================================

        pillar = str(
            event.pillar
        ).lower().strip()

        attribute = self.get_pillar_attribute(
            pillar
        )

        # ======================================================
        # SCORE ANTES
        # ======================================================

        score_before = self.get_attribute(
            individual,
            attribute,
            50
        )

        # ======================================================
        # PERCEPÇÃO
        # ======================================================

        perception = self.perceive_event(
            individual,
            event
        )

        # ======================================================
        # DECISÃO
        # ======================================================

        action = self.choose_event_action(
            individual,
            event,
            perception
        )

        # ======================================================
        # APLICA AÇÃO
        # ======================================================

        self.apply_event_action(
            individual,
            event,
            action
        )

        # ======================================================
        # SCORE DEPOIS
        # ======================================================

        score_after = self.get_attribute(
            individual,
            attribute,
            50
        )

        # ======================================================
        # ESTADO ATUAL
        # ======================================================

        individual.perception = (
            perception["description"]
        )

        individual.last_action = action

        # ======================================================
        # HISTÓRICO
        # ======================================================

        if hasattr(
            individual,
            "register_action"
        ):

            individual.register_action(
                day,
                event,
                perception["description"],
                action,
                event.pillar,
                score_before,
                score_after
            )

        # ======================================================
        # RETORNO
        # ======================================================

        return {
            "individual": individual.name,
            "day": day,
            "event": getattr(
                event,
                "name",
                "Evento"
            ),
            "pillar": event.pillar,
            "perception_score": perception["score"],
            "perception": perception["description"],
            "action": action,
            "before": score_before,
            "after": score_after
        }

    # ==========================================================
    # INTERAÇÕES INDIVÍDUO-INDIVÍDUO
    # ==========================================================

    def simulate_interactions(
        self,
        day
    ):

        """
        Realiza interações entre indivíduos.

        Aproximadamente metade da população
        participa de uma interação por dia.
        """

        if len(
            self.individuals
        ) < 2:

            return

        number_of_interactions = max(
            1,
            len(self.individuals) // 2
        )

        for _ in range(
            number_of_interactions
        ):

            individual_a, individual_b = random.sample(
                self.individuals,
                2
            )

            self.interact(
                individual_a,
                individual_b,
                day
            )

    # ==========================================================
    # INTERAÇÃO
    # ==========================================================

    def interact(
        self,
        individual_a,
        individual_b,
        day
    ):

        """
        Simula uma interação social entre dois indivíduos.

        A compatibilidade é baseada no score social
        de cada indivíduo.
        """

        # ======================================================
        # SCORES
        # ======================================================

        score_a = self.get_social_score(
            individual_a
        )

        score_b = self.get_social_score(
            individual_b
        )

        # ======================================================
        # COMPATIBILIDADE
        # ======================================================

        compatibility = (
            score_a
            + score_b
        ) / 2

        # ======================================================
        # DIFERENÇA
        # ======================================================

        difference = abs(
            score_a
            - score_b
        )

        # ======================================================
        # SCORE DA INTERAÇÃO
        # ======================================================

        interaction_score = (
            compatibility * 0.70
            + (100 - difference) * 0.30
        )

        # ======================================================
        # ALEATORIEDADE
        # ======================================================

        interaction_score += random.uniform(
            -10,
            10
        )

        interaction_score = self.clamp(
            interaction_score
        )

        # ======================================================
        # INTERAÇÃO POSITIVA
        # ======================================================

        if interaction_score >= 65:

            interaction_type = "positiva"

            # Respeito
            if hasattr(
                individual_a,
                "respeito"
            ):

                individual_a.respeito = self.clamp(
                    individual_a.respeito + 0.15
                )

            if hasattr(
                individual_b,
                "respeito"
            ):

                individual_b.respeito = self.clamp(
                    individual_b.respeito + 0.15
                )

            # Confiança
            if hasattr(
                individual_a,
                "trust"
            ):

                individual_a.trust = self.clamp(
                    individual_a.trust + 0.25
                )

            if hasattr(
                individual_b,
                "trust"
            ):

                individual_b.trust = self.clamp(
                    individual_b.trust + 0.25
                )

            # Bem-estar
            if hasattr(
                individual_a,
                "wellbeing"
            ):

                individual_a.wellbeing = self.clamp(
                    individual_a.wellbeing + 0.10
                )

            if hasattr(
                individual_b,
                "wellbeing"
            ):

                individual_b.wellbeing = self.clamp(
                    individual_b.wellbeing + 0.10
                )

        # ======================================================
        # CONFLITO
        # ======================================================

        elif interaction_score < 35:

            interaction_type = "conflito"

            # Confiança
            if hasattr(
                individual_a,
                "trust"
            ):

                individual_a.trust = self.clamp(
                    individual_a.trust - 0.25
                )

            if hasattr(
                individual_b,
                "trust"
            ):

                individual_b.trust = self.clamp(
                    individual_b.trust - 0.25
                )

            # Bem-estar
            if hasattr(
                individual_a,
                "wellbeing"
            ):

                individual_a.wellbeing = self.clamp(
                    individual_a.wellbeing - 0.15
                )

            if hasattr(
                individual_b,
                "wellbeing"
            ):

                individual_b.wellbeing = self.clamp(
                    individual_b.wellbeing - 0.15
                )

        # ======================================================
        # INTERAÇÃO NEUTRA
        # ======================================================

        else:

            interaction_type = "neutra"

        # ======================================================
        # REGISTRO
        # ======================================================

        interaction = {

            "day": day,

            "individual_a": (
                individual_a.name
            ),

            "individual_b": (
                individual_b.name
            ),

            "type": interaction_type,

            "score": interaction_score
        }

        self.interactions.append(
            interaction
        )

        self.total_interactions += 1

        return interaction

    # ==========================================================
    # SCORE SOCIAL
    # ==========================================================

    def get_social_score(
        self,
        individual
    ):

        """
        Calcula o score social médio.

        Os seis pilares possuem o mesmo peso.
        """

        pillars = [

            "respeito",

            "cidadania",

            "responsabilidade",

            "zelo",

            "justica",

            "sinceridade"

        ]

        values = []

        for pillar in pillars:

            if hasattr(
                individual,
                pillar
            ):

                values.append(
                    getattr(
                        individual,
                        pillar
                    )
                )

        if not values:

            return 50

        return sum(
            values
        ) / len(values)

    # ==========================================================
    # SCORE DOS PILARES
    # ==========================================================

    def get_pillar_scores(
        self,
        individual
    ):

        """
        Retorna os seis pilares do indivíduo.
        """

        return {

            "respeito": self.get_attribute(
                individual,
                "respeito"
            ),

            "cidadania": self.get_attribute(
                individual,
                "cidadania"
            ),

            "responsabilidade": self.get_attribute(
                individual,
                "responsabilidade"
            ),

            "zelo": self.get_attribute(
                individual,
                "zelo"
            ),

            "justiça": self.get_attribute(
                individual,
                "justica"
            ),

            "sinceridade": self.get_attribute(
                individual,
                "sinceridade"
            )

        }

    # ==========================================================
    # MOSTRAR INTERAÇÕES
    # ==========================================================

    def show_interactions(
        self,
        amount=15
    ):

        """
        Mostra as últimas interações.
        """

        print("\n")
        print("=" * 75)
        print("🤝 INTERAÇÕES SOCIAIS")
        print("=" * 75)

        if not self.interactions:

            print(
                "\nNenhuma interação foi realizada."
            )

            return

        for interaction in self.interactions[-amount:]:

            print(
                f"Dia {interaction['day']:3} | "
                f"{interaction['individual_a']:<15} ↔ "
                f"{interaction['individual_b']:<15} | "
                f"{interaction['type']:<10} | "
                f"Score: "
                f"{interaction['score']:.2f}"
            )

    # ==========================================================
    # MOSTRAR PILARES
    # ==========================================================

    def show_population_scores(self):

        """
        Mostra os scores sociais da população.
        """

        print("\n")
        print("=" * 85)
        print("📊 PILARES DA SOCIEDADE")
        print("=" * 85)

        for individual in self.individuals:

            scores = self.get_pillar_scores(
                individual
            )

            social_score = self.get_social_score(
                individual
            )

            print(
                f"\n{individual.name}"
            )

            print(
                f"  Respeito:          {scores['respeito']:.2f}"
            )

            print(
                f"  Cidadania:         {scores['cidadania']:.2f}"
            )

            print(
                f"  Responsabilidade: {scores['responsabilidade']:.2f}"
            )

            print(
                f"  Zelo:              {scores['zelo']:.2f}"
            )

            print(
                f"  Justiça:           {scores['justiça']:.2f}"
            )

            print(
                f"  Sinceridade:       {scores['sinceridade']:.2f}"
            )

            print(
                f"  Score Social:      {social_score:.2f}"
            )