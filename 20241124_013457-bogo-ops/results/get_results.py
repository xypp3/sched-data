import pandas as pd
import re


def parse_stress_ng_log(log_content):
    """
    Parse stress-ng log content and extract the metrics row into a pandas DataFrame

    Parameters:
    log_content (str): The content of the stress-ng log file

    Returns:
    pandas.DataFrame: DataFrame containing the metrics
    """
    # Split the log into lines
    lines = log_content.split("\n")

    # Find the process ID from the first line
    first_line = lines[0]
    pid_match = re.search(r"\[(\d+)\]", first_line)
    if not pid_match:
        raise ValueError("Could not find process ID in log file")
    process_id = pid_match.group(0)  # Including the brackets

    # Find the metrics header and data lines
    metrics_data = None

    for i, line in enumerate(lines):
        if "stressor       bogo ops" in line:
            metrics_data = lines[i + 2]
            break

    if metrics_data is None:
        raise ValueError("Could not find metrics data in log content")

    # Define the columns we expect based on the log format
    columns = [
        "stressor",
        "bogo_ops",
        "real_time",
        "usr_time",
        "sys_time",
        "bogo_ops_real_time",
        "bogo_ops_usr_sys_time",
        "cpu_used_per_instance",
        "rss_max",
    ]

    # Extract just the data part after the process ID
    data = metrics_data.split(process_id)[1].strip()

    # Split the data while preserving whitespace for the stressor name
    parts = data.split()

    # Create a single row of data
    row_data = [
        parts[0],  # stressor
        float(parts[1]),  # bogo_ops
        float(parts[2]),  # real_time
        float(parts[3]),  # usr_time
        float(parts[4]),  # sys_time
        float(parts[5]),  # bogo_ops_real_time
        float(parts[6]),  # bogo_ops_usr_sys_time
        float(parts[7]),  # cpu_used_per_instance
        float(parts[8]),  # rss_max
    ]

    # Create DataFrame with a single row
    df = pd.DataFrame([row_data], columns=columns)

    return df


def main():
    # Input and output file paths
    scheds = ["default", "lavd", "rusty", "rustland"]
    benchmarks = [
        "/cpu24_io0/stressng_cpu_output",
        "/cpu18_io6/stressng_cpu_output",
        "/cpu18_io6/stressng_io_output",
        "/cpu12_io12/stressng_cpu_output",
        "/cpu12_io12/stressng_io_output",
        "/cpu6_io18/stressng_cpu_output",
        "/cpu6_io18/stressng_io_output",
        "/cpu0_io24/stressng_io_output",
    ]
    for sched in scheds:
        for bench in benchmarks:
            input_file = sched + bench + ".txt"
            output_file = sched + bench + ".csv"

            try:
                # Read the local file
                with open(input_file, "r") as f:
                    log_content = f.read()

                # Parse the log content
                df = parse_stress_ng_log(log_content)

                # Save to CSV
                df.to_csv(output_file, index=False)

                print(f"\nExtracted metrics as DataFrame:")
                print(df)
                print(f"\nMetrics saved to {output_file}")

            except FileNotFoundError:
                print(f"Error: Could not find input file: {input_file}")
            except ValueError as e:
                print(f"Error parsing log content: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
