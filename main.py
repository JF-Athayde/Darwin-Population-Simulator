from darwin.population import Population
from darwin.visualization import Visualization
from create_pdf import create_pdf


def show_winner(population):

    # Ordena os indivíduos pela pontuação social
    ranking = sorted(
        population.individuals,
        key=lambda individual: individual.social_score(),
        reverse=True
    )

    winner = ranking[0]

    print("\n")
    print("=" * 70)
    print("🏆 RESULTADO FINAL")
    print("=" * 70)

    print("\n🥇 INDIVÍDUO MAIS SOCIAL")
    print(f"Nome: {winner.name}")
    print(f"Pontuação social: {winner.social_score():.2f}")

    print("\n" + "-" * 70)
    print("📊 RANKING")
    print("-" * 70)

    for position, individual in enumerate(ranking[:10], 1):
        print(
            f"{position:2}º | "
            f"{individual.name:<15} | "
            f"{individual.social_score():.2f}"
        )

    # Mostra o relatório no terminal
    winner.show_full_report()

    return winner


def main():

    print("=" * 70)
    print("DARWIN POPULATION")
    print("EVOLUÇÃO DOS COMPORTAMENTOS EM SOCIEDADE")
    print("=" * 70)

    # ==========================================================
    # CONFIGURAÇÃO
    # ==========================================================

    TAMANHO_POPULACAO = 1000
    DIAS = 200

    # ==========================================================
    # CRIA POPULAÇÃO
    # ==========================================================

    population = Population(TAMANHO_POPULACAO)

    print("\nPopulação criada!")
    print(f"Indivíduos: {len(population.individuals)}")

    # ==========================================================
    # SIMULAÇÃO
    # ==========================================================

    print("\nIniciando simulação...")
    print(f"Duração: {DIAS} dias")

    population.simulate(DIAS)

    print("\nSimulação finalizada!")

    # ==========================================================
    # STATUS
    # ==========================================================

    population.show_status()

    # ==========================================================
    # INTERAÇÕES
    # ==========================================================

    population.social.show_interactions(15)

    # ==========================================================
    # VENCEDOR
    # ==========================================================

    winner = show_winner(population)

    # ==========================================================
    # GRÁFICOS
    # ==========================================================

    visualization = Visualization(population)

    visualization.plot_pillars()
    visualization.plot_wellbeing()

    if hasattr(visualization, "plot_winner_profile"):
        visualization.plot_winner_profile(winner)

    # ==========================================================
    # PDF
    # ==========================================================

    print("\n")
    print("=" * 70)
    print("📄 GERANDO RELATÓRIO PDF")
    print("=" * 70)

    create_pdf(
        population,
        "relatorio_darwin_population.pdf",
        DIAS
    )

    print("\n✅ PDF criado com sucesso!")


if __name__ == "__main__":
    main()
