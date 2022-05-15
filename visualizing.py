import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as colors
import random

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def draw_graph(bins1, bins2, S):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(211)

    for x in bins1.keys():
        r = random.random()
        b = random.random()
        g = random.random()
        color = (r, g, b)
        for idx, i in enumerate(bins1[x].values()):
            # ax1.add_patch(
            #         patches.Rectangle((idx-0.5, min(i)), 1, max(i)-min(i), color=color, alpha=.5)
            #         )
            ax1.violinplot(i, positions=[idx])

    ax1.plot(S, alpha=.5, color="black")
    ax1.grid(True)
    ax1.set_ylim((0,200))
    ax1.set_xlim((0, 102))
    ax1.set_xlabel("timesteps")
    ax1.set_ylabel("index lvl")

    if bins2:
        ax2 = fig1.add_subplot(212)
        for x in bins2.keys():
            r = random.random()
            b = random.random()
            g = random.random()
            color = (r, g, b)
            for idx, i in enumerate(bins2[x].values()):
                # ax2.add_patch(
                #         patches.Rectangle((idx-0.5, min(i)), 1, max(i)-min(i), color=color, alpha=.5)
                #         )
                ax2.violinplot(i, positions=[idx])

        ax2.plot(S, alpha=.5, color="black")
        ax2.grid(True)
        ax2.set_ylim((0,200))
        ax2.set_xlim((0, 102))
        ax2.set_xlabel("timesteps")
        ax2.set_ylabel("index lvl")

    plt.tight_layout()
    #plt.figtext(0, 0.001, "time m1: \ntime m2:", wrap=True)
    plt.show()

def draw_overlap(bins1, bins2, S=None, bin=[0], label= ["bins1", "bins2"], title=""):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(211)
    for x in bins1.keys(): #bins
        if x in ["".join(["bin", str(i)]) for i in bin]:
            for idx, (i, j) in enumerate(zip(bins1[x].values(), bins2[x].values())): #idx=t
                    ax1.add_patch(
                            patches.Rectangle((idx-0.5, min(i)), 0.5, max(i)-min(i), color=(1.0, 0.84, 0.17), alpha=0.5, label=label[0] if idx==0 else None)
                            )
                    ax1.add_patch(
                            patches.Rectangle((idx, min(j)), 0.5, max(j)-min(j), color=(0.35, 0.36, 0.91), alpha=0.5, label=label[1] if idx==0 else None)
                            )
    if S is not None:
        ax1.plot(S, alpha=.5, color="black")
    ax1.grid(True)
    ax1.set_ylim((0,200))
    ax1.set_xlim((0, 102))
    ax1.set_xlabel("timesteps")
    ax1.set_ylabel("index lvl")
    fig1.legend(loc=7)
    plt.title(title)
    plt.tight_layout()
    #plt.figtext(0, 0.001, "time m1: \ntime m2:", wrap=True)
    plt.show()

def draw_diffs(diffs_dict):
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    for bin in diffs_dict.keys():
        ax1.plot(diffs_dict[bin], label=f"{bin}")
    ax1.set_xlabel("timesteps")
    ax1.set_ylabel("absolute difference")
    fig1.legend(loc=7)
    plt.show()
