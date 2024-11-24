import pandas as pd
import re


def parse_stress_ng_log(log_content):
    lines = log_content.split("\n")

    # Find the process ID from the first line
    first_line = lines[0]
    pid_match = re.search(r"\[(\d+)\]", first_line)
    if not pid_match:
        raise ValueError("Could not find process ID in log file")
    process_id = pid_match.group(0)  # Including the brackets

    metrics_data = None

    for i, line in enumerate(lines):
        if "stressor       bogo ops" in line:
            metrics_data = lines[i + 2]
            break

    if metrics_data is None:
        raise ValueError("Could not find metrics data in log content")

    columns = [
        "stressor",
        "bogo_ops",
        "real_time",
        "usr_time",
        "sys_time",
        "bogo_ops_real_time",
        "bogo_ops_usr_sys_time",
    ]

    # Extract just the data part after the process ID
    data = metrics_data.split(process_id)[1].strip()

    # Split the data while preserving whitespace for the stressor name
    parts = data.split()

    row_data = [
        parts[0],  # stressor
        float(parts[1]),  # bogo_ops
        float(parts[2]),  # real_time
        float(parts[3]),  # usr_time
        float(parts[4]),  # sys_time
        float(parts[5]),  # bogo_ops_real_time
        float(parts[6]),  # bogo_ops_usr_sys_time
    ]

    df = pd.DataFrame([row_data], columns=columns)

    return df


def main():
    # Input and output file paths
    scheds = ["default", "lavd", "rusty", "rustland"]
    benchmarks = [
        {"cpu": "/cpu24_io0/stressng_cpu_output.txt", "io": ""},
        {
            "cpu": "/cpu18_io6/stressng_cpu_output.txt",
            "io": "/cpu18_io6/stressng_io_output.txt",
        },
        {
            "cpu": "/cpu12_io12/stressng_cpu_output.txt",
            "io": "/cpu12_io12/stressng_io_output.txt",
        },
        {
            "cpu": "/cpu6_io18/stressng_cpu_output.txt",
            "io": "/cpu6_io18/stressng_io_output.txt",
        },
        {"cpu": "", "io": "/cpu0_io24/stressng_io_output.txt"},
    ]

    for sched in scheds:
        for bench in benchmarks:
            out_path = ""
            cpu_val = 0
            io_val = 0
            for kind, path in bench.items():
                if path == "":
                    continue
                with open(f"{sched}{path}", "r") as file:
                    data = file.read()
                    if "cpu" == kind:
                        cpu_val = parse_stress_ng_log(data)["bogo_ops_real_time"]
                    elif "io":
                        io_val = parse_stress_ng_log(data)["bogo_ops_real_time"]

                out_path = path.split("/")[1]

            # after processing
            new_df = pd.DataFrame(
                {
                    "cpu_realtime": cpu_val,
                    "io_realtime": io_val,
                }
            )

            output_file = sched + "/" + out_path + "/bogo.csv"
            new_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
