from railway_simulation import main_menu, simulation

if __name__ == "__main__":
    stations, t1_start, t1_dest, t2_start, t2_dest, t3_start, t3_dest, utility_mode = main_menu()
    simulation(stations, t1_start, t1_dest, t2_start, t2_dest, t3_start, t3_dest, utility_mode)
