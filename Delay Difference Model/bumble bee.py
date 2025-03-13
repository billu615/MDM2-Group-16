import matplotlib.pyplot as plt
import numpy as np

# make latex font
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.serif": ["Times New Roman","Times","Palatino", "serif"],
    "font.size": 24,
    "legend.fontsize": 19
})

T = 250 # days
K = 860  # maximum population
daily_egg = 20  # spawn per day

# stage delay days
dur_E = 5
dur_L = 18
dur_P = 14
dur_H = 5
dur_F = 48

s_E = 0.97
s_L = 0.99
s_P = 0.999
s_H = 0.985
s_F = 0.9495

food_collect_per_F = 0.3  # food collection (g)
# daily food consumption (g)
c_L = 0.042  # Larvae
c_H = 0.2365 # Hive
c_F = 0.2365  # Forager

# initial food
S0 = 5000

# parameters for pesticide
LD50 = 0.014  # LD50 (µg/bee)
pesticide_conc = 0.02415  # 24.15 ppb -> 0.02415 µg/g
half_life = 148  # pesticide half life (days)
d_factor = (0.5) ** (1 / half_life)
hill_n = 2  # Hill coef


def hill_mortality(dose, ld50=LD50, n=hill_n):
	# dose measured as µg/bee
	return dose ** n / (ld50 ** n + dose ** n)


# without pesticide
egg_queue = [0.0 for _ in range(dur_E)]
larvae_queue = [0.0 for _ in range(dur_L)]
pupae_queue = [0.0 for _ in range(dur_P)]
hive_queue = [0.0 for _ in range(dur_H)]
forager_queue = [0.0 for _ in range(dur_F)]

days = []
E_pop = []
L_pop = []
P_pop = []
H_pop = []
F_pop = []
N_pop = []
S_series = []

# initial food
S = S0

for n in range(T):
	total_E = sum(egg_queue)
	total_L = sum(larvae_queue)
	total_P = sum(pupae_queue)
	total_H = sum(hive_queue)
	total_F = sum(forager_queue)

	N = total_E + total_L + total_P + total_H + total_F  # total population

	E_new = daily_egg * max(0, 1 - N / K)

	# food comsumption
	D = c_L * total_L + c_H * total_H + c_F * total_F
	eta = 1.0 if D == 0 else max(0, min(1.0, S / D))

	if S < 0:
		S = 0

	# food remain
	S = S + food_collect_per_F * total_F - D

	days.append(n)
	E_pop.append(total_E)
	L_pop.append(total_L)
	P_pop.append(total_P)
	H_pop.append(total_H)
	F_pop.append(total_F)
	N_pop.append(N)
	S_series.append(S)

	# update population queues
	egg_queue = [x * s_E for x in egg_queue]
	larvae_queue = [x * (s_L * eta) for x in larvae_queue]
	pupae_queue = [x * s_P for x in pupae_queue]
	hive_queue = [x * (s_H * eta) for x in hive_queue]
	forager_queue = [x * (s_F * eta) for x in forager_queue]

	conv_E_to_L = egg_queue.pop(0)
	conv_L_to_P = larvae_queue.pop(0)
	conv_P_to_H = pupae_queue.pop(0)
	conv_H_to_F = hive_queue.pop(0)
	conv_F_leave = forager_queue.pop(0)

	larvae_queue.append(conv_E_to_L)
	pupae_queue.append(conv_L_to_P)
	hive_queue.append(conv_P_to_H)
	forager_queue.append(conv_H_to_F)

	egg_queue.append(E_new)

final_E = sum(egg_queue)
final_L = sum(larvae_queue)
final_P = sum(pupae_queue)
final_H = sum(hive_queue)
final_F = sum(forager_queue)
final_N = final_E + final_L + final_P + final_H + final_F
final_S = S

print("[Original Model] Final Population in Each Stage:")
print(f"Egg: {final_E:.2f}")
print(f"Larvae: {final_L:.2f}")
print(f"Pupae: {final_P:.2f}")
print(f"Drone: {final_H:.2f}")
print(f"Worker: {final_F:.2f}")
print(f"Total Population (N): {final_N:.2f}")
print(f"Remaining Food (S): {final_S:.2f} g")


egg_queue_p = [0.0 for _ in range(dur_E)]
larvae_queue_p = [0.0 for _ in range(dur_L)]
pupae_queue_p = [0.0 for _ in range(dur_P)]
hive_queue_p = [0.0 for _ in range(dur_H)]
forager_queue_p = [0.0 for _ in range(dur_F)]

egg_cum = [0.0 for _ in range(dur_E)]
larvae_cum = [0.0 for _ in range(dur_L)]
pupae_cum = [0.0 for _ in range(dur_P)]
hive_cum = [0.0 for _ in range(dur_H)]
forager_cum = [0.0 for _ in range(dur_F)]

for i in range(dur_E):
	egg_queue_p[i] = 0.0
	egg_cum[i] = 0.0
for i in range(dur_L):
	larvae_queue_p[i] = 0.0
	larvae_cum[i] = 0.0
for i in range(dur_P):
	pupae_queue_p[i] = 0.0
	pupae_cum[i] = 0.0
for i in range(dur_H):
	hive_queue_p[i] = 0.0
	hive_cum[i] = 0.0
for i in range(dur_F):
	forager_queue_p[i] = 0.0
	forager_cum[i] = 0.0


days_p = []
E_pop_p = []
L_pop_p = []
P_pop_p = []
H_pop_p = []
F_pop_p = []
N_pop_p = []
S_series_p = []
Pest_series = []

S_p = S0
pesticide = 50  # measured as \mu g

# with pesticide
for n in range(T):
	total_E_p = sum(egg_queue_p)
	total_L_p = sum(larvae_queue_p)
	total_P_p = sum(pupae_queue_p)
	total_H_p = sum(hive_queue_p)
	total_F_p = sum(forager_queue_p)

	N_p = total_E_p + total_L_p + total_P_p + total_H_p + total_F_p  # total population


	E_new_p = daily_egg * max(0, 1 - N_p / K)

	# food comsumption
	D_p = c_L * total_L_p + c_H * total_H_p + c_F * total_F_p
	eta_p = 1.0 if D_p == 0 else max(0, min(1.0, S_p / D_p))
	if S_p < 0:
		S_p = 0

	# Food remain
	S_p = S_p + food_collect_per_F * total_F_p - D_p

	# update pesticide changes
	pesticide = pesticide * d_factor
	pesticide_conc = pesticide_conc * d_factor
	delta_S_p = food_collect_per_F * total_F_p
	delta_P_new = pesticide_conc * delta_S_p
	delta_P_consumed = pesticide * (D_p / S_p) if S_p > 0 else 0
	pesticide = pesticide - delta_P_consumed + delta_P_new
	Pest_series.append(pesticide)
	Cp = pesticide / S_p if S_p > 0 else 0  # pesticide concentration

	# pesticide daily intake
	dose_L = c_L * Cp
	dose_H = c_H * Cp
	dose_F = c_F * Cp

	days_p.append(n)
	E_pop_p.append(total_E_p)
	L_pop_p.append(total_L_p)
	P_pop_p.append(total_P_p)
	H_pop_p.append(total_H_p)
	F_pop_p.append(total_F_p)
	N_pop_p.append(N_p)
	S_series_p.append(S_p)

	# update population queues and pesticide cumulative
	# Egg (without food intake)
	egg_queue_p = [x * s_E for x in egg_queue_p]
	egg_cum = [0.0 for _ in egg_cum]

	# Larvae
	new_larvae_queue = []
	new_larvae_cum = []
	for x, q in zip(larvae_queue_p, larvae_cum):
		new_q = q + dose_L
		mu_this = hill_mortality(new_q)
		new_x = x * s_L * eta_p * (1 - mu_this)
		new_larvae_queue.append(new_x)
		new_larvae_cum.append(new_q)
	larvae_queue_p = new_larvae_queue
	larvae_cum = new_larvae_cum

	# Pupae (without food intake)
	pupae_queue_p = [x * s_P for x in pupae_queue_p]
	pupae_cum = [0.0 for _ in pupae_cum]

	# Hive
	new_hive_queue = []
	new_hive_cum = []
	for x, q in zip(hive_queue_p, hive_cum):
		new_q = q + dose_H
		mu_this = hill_mortality(new_q)
		new_x = x * s_H * eta_p * (1 - mu_this)
		new_hive_queue.append(new_x)
		new_hive_cum.append(new_q)
	hive_queue_p = new_hive_queue
	hive_cum = new_hive_cum

	# Forager
	new_forager_queue = []
	new_forager_cum = []
	for x, q in zip(forager_queue_p, forager_cum):
		new_q = q + dose_F
		mu_this = hill_mortality(new_q)
		new_x = x * s_F * eta_p * (1 - mu_this)
		new_forager_queue.append(new_x)
		new_forager_cum.append(new_q)
	forager_queue_p = new_forager_queue
	forager_cum = new_forager_cum

	# Egg -> Larvae
	conv_E_to_L_p = egg_queue_p.pop(0)
	conv_E_cum = egg_cum.pop(0)
	# Larvae -> Pupae
	conv_L_to_P_p = larvae_queue_p.pop(0)
	conv_L_cum = larvae_cum.pop(0)
	# Pupae -> Hive
	conv_P_to_H_p = pupae_queue_p.pop(0)
	conv_P_cum = pupae_cum.pop(0)
	# Hive -> Forager
	conv_H_to_F_p = hive_queue_p.pop(0)
	conv_H_cum = hive_cum.pop(0)

	conv_F_leave_p = forager_queue_p.pop(0)
	conv_F_cum = forager_cum.pop(0)

	# transfer to next stage
	larvae_queue_p.append(conv_E_to_L_p)
	larvae_cum.append(conv_E_cum)
	pupae_queue_p.append(conv_L_to_P_p)
	pupae_cum.append(conv_L_cum)
	hive_queue_p.append(conv_P_to_H_p)
	hive_cum.append(conv_P_cum)
	forager_queue_p.append(conv_H_to_F_p)
	forager_cum.append(conv_H_cum)

	egg_queue_p.append(E_new_p)
	egg_cum.append(0.0)

# Final population
final_E_p = sum(egg_queue_p)
final_L_p = sum(larvae_queue_p)
final_P_p = sum(pupae_queue_p)
final_H_p = sum(hive_queue_p)
final_F_p = sum(forager_queue_p)
final_N_p = final_E_p + final_L_p + final_P_p + final_H_p + final_F_p
final_S_p = S_p

# Pesticide intake
avg_larvae = np.mean(larvae_cum) if len(larvae_cum) > 0 else 0
avg_hive = np.mean(hive_cum) if len(hive_cum) > 0 else 0
avg_forager = np.mean(forager_cum) if len(forager_cum) > 0 else 0

print("\n[With Pesticide Impact] Final Population in Each Stage:")
print(f"Egg: {final_E_p:.2f}")
print(f"Larvae: {final_L_p:.2f}  (Avg cumulative pesticide: {avg_larvae:.4f} µg/bee)")
print(f"Pupae: {final_P_p:.2f}")
print(f"Drone: {final_H_p:.2f}  (Avg cumulative pesticide: {avg_hive:.4f} µg/bee)")
print(f"Worker: {final_F_p:.2f}  (Avg cumulative pesticide: {avg_forager:.4f} µg/bee)")
print(f"Total Population (N): {final_N_p:.2f}")
print(f"Remaining Food (S): {final_S_p:.2f} g")
print(f"Total Pesticide in Food: {pesticide:.4f} µg, Pesticide Concentration: {Cp:.6f} µg/g")



# visualization
plt.figure(figsize=(12, 8))
plt.plot(days, E_pop, label='Egg')
plt.plot(days, L_pop, label='Larvae')
plt.plot(days, P_pop, label='Pupae')
plt.plot(days, H_pop, label='Drone')
plt.plot(days, F_pop, label='Worker')
plt.xlabel("Days")
plt.ylabel("Population")
plt.title("Bumble Bee Population Dynamics Across Stages (Without Pesticide)")
plt.legend()
plt.grid(True)
# plt.ylim(0, 18750)
plt.tight_layout()
plt.show()


plt.figure(figsize=(12, 8))
plt.plot(days_p, E_pop_p, label='Egg')
plt.plot(days_p, L_pop_p, label='Larvae')
plt.plot(days_p, P_pop_p, label='Pupae')
plt.plot(days_p, H_pop_p, label='Drone')
plt.plot(days_p, F_pop_p, label='Worker')
plt.xlabel("Days")
plt.ylabel("Population")
plt.title("Bumble Bee Population Dynamics Across Stages (With Pesticide)")
plt.legend()
plt.grid(True)
# plt.ylim(0, 18750)
plt.tight_layout()
plt.show()


plt.figure(figsize=(12, 8))
plt.plot(days, N_pop, label='Total Population (Without Pesticide)', linewidth=2)
plt.plot(days_p, N_pop_p, label='Total Population (With Pesticide)', linewidth=2)
plt.xlabel("Days")
plt.ylabel("Total Population")
plt.title("Comparison of Total Bumble Bee Population")
plt.legend(loc = 'lower right')
plt.grid(True)
plt.tight_layout()
plt.show()
