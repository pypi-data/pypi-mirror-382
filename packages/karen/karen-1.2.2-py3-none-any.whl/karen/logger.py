import csv

def logCombo(combo):
    times_logged = {}

    try:
        with open("combo_logs.csv", newline="", mode="r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",", quotechar="|")
            times_logged = {row[0] : row[1] for row in csv_reader}
    
    except:
        print("Failed to open combo_logs.csv, the file will be created")

    if combo in times_logged:
        times_logged[combo] = 1 + int(times_logged[combo])
    else:
        times_logged[combo] = 1

    with open("combo_logs.csv", newline="", mode="w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL)
        for combo in times_logged:
            csv_writer.writerow([combo, times_logged[combo]])