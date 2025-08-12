import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from darwin.population import Population

def print_status(pop):
    print("Status inicial dos indivíduos:")
    for ind in pop.individuals:
        print(f"{ind.name} | HP: {ind.hp:.1f} | STR: {ind.strength:.2f} | SPD: {ind.speed:.2f} | CHA: {ind.charisma:.2f}")

def get_color(value, vmin=0, vmax=10, cmap_name='YlOrRd'):
    # Normaliza valor para [0,1]
    norm_val = (value - vmin) / (vmax - vmin)
    cmap = cm.get_cmap(cmap_name)
    rgba = cmap(norm_val)
    # Converte rgba para hex
    return plt.colors.rgb2hex(rgba)

def plot_population_and_table(pop, ax_bar, ax_table):
    stats = pop.get_population_stats()

    order = np.argsort(stats['hp'])[::-1]

    names = [stats['names'][i] for i in order]
    hp = [stats['hp'][i] for i in order]
    strength = [stats['strength'][i] for i in order]
    speed = [stats['speed'][i] for i in order]
    luck = [stats['luck'][i] for i in order]
    smart = [stats['smart'][i] for i in order]
    dexterity = [stats['dexterity'][i] for i in order]
    wisdom = [stats['wisdom'][i] for i in order]
    charisma = [stats['charisma'][i] for i in order]
    beauty = [stats['beauty'][i] for i in order]
    overall = [stats['overall'][i] for i in order]
    kills = [stats.get('kills', [0]*len(names))[i] for i in order]

    cmap = plt.get_cmap('tab20')
    colors = [cmap(i % 20) for i in range(len(names))]

    ax_bar.clear()
    bars = ax_bar.bar(names, hp, color=colors)
    ax_bar.set_ylim(0, 120)
    ax_bar.set_title('HP of Individuals (sorted)')
    ax_bar.set_xlabel('Individuals')
    ax_bar.set_ylabel('HP')
    ax_bar.tick_params(axis='x', rotation=45)

    for bar, val in zip(bars, hp):
        ax_bar.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 5,
                    f'{val:.1f}', ha='center', color='white', fontsize=8)

    table_data = []
    headers = ['Name', 'HP', 'STR', 'SPD', 'LUCK', 'SMART', 'DEX', 'WIS', 'CHA', 'BEAUTY', 'OVR', 'KILLS']

    for i in range(len(names)):
        row = [
            names[i],
            f"{hp[i]:.3f}",
            f"{strength[i]:.3f}",
            f"{speed[i]:.3f}",
            f"{luck[i]:.3f}",
            f"{smart[i]:.3f}",
            f"{dexterity[i]:.3f}",
            f"{wisdom[i]:.3f}",
            f"{charisma[i]:.3f}",
            f"{beauty[i]:.3f}",
            f"{overall[i]:.3f}",
            str(kills[i])
        ]
        table_data.append(row)

    ax_table.clear()
    ax_table.axis('off')
    table = ax_table.table(cellText=table_data, colLabels=headers, loc='center', cellLoc='center')

    for i, color in enumerate(colors):
        for j in range(len(headers)):
            cell = table[(i+1, j)]
            cell.set_facecolor(color)
            cell.set_text_props(color='black', weight='bold')

    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1, 1.5)

    plt.tight_layout()
    plt.pause(0.5)

def main():
    size = 20
    bounds = (0, 10)
    less = 0.001

    pop = Population(size, bounds, less)

    print_status(pop)

    plt.ion()
    fig, (ax_bar, ax_table) = plt.subplots(1, 2, figsize=(15, 6))

    while True:
        pop.simulate_day()
        plot_population_and_table(pop, ax_bar, ax_table)

        # Verifica se só sobrou 1 indivíduo
        if len(pop.individuals) == 1:
            winner = pop.individuals[0]
            print("\n*** Rodada finalizada! Vencedor: ***")
            print(f"Nome: {winner.name}")
            print(f"HP: {winner.hp:.3f}")
            print(f"Strength: {winner.strength:.3f}")
            print(f"Speed: {winner.speed:.3f}")
            print(f"Luck: {winner.luck:.3f}")
            print(f"Smart: {winner.smart:.3f}")
            print(f"Dexterity: {winner.dexterity:.3f}")
            print(f"Wisdom: {winner.wisdom:.3f}")
            print(f"Charisma: {winner.charisma:.3f}")
            print(f"Beauty: {winner.beauty:.3f}")
            print(f"Overall: {winner.ovr:.3f}")
            print(f"Kills: {getattr(winner, 'kills', 0)}")
            break

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    main()
