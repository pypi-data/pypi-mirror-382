from omgui.spf import spf
import pandas as pd
import random


def generate_df_1(rows=10):
    """
    Generate a DataFrame with column names.
    """
    names = [f"Person {i}" for i in range(rows)]
    ages = [random.randint(18, 60) for _ in range(rows)]
    heights = [random.randint(150, 200) for _ in range(rows)]
    df = pd.DataFrame({"name": names, "age": ages, "height": heights})
    return df


def generate_df_2(rows=100):
    """
    Generate a DataFrame without solumn names.
    """
    names = [f"Person {i}" for i in range(rows)]
    ages = [random.randint(18, 60) for _ in range(rows)]
    heights = [random.randint(150, 200) for _ in range(rows)]
    data_rows = list(zip(names, ages, heights))
    df = pd.DataFrame(data_rows, columns=None)
    return df


df1 = generate_df_1()
df2 = generate_df_2()


# Print table directly
spf("\n<h1>Simple table print</h1>")
spf.table(generate_df_1(10))
spf.table(generate_df_2(10))

# -- BREAK --
if input("Press ENTER to see table returned for later use..."):
    print("OK")

# Produce table for later use
table2 = spf.table.produce(generate_df_2(10))
print(table2)

# -- BREAK --
if input("Press ENTER to see paginated table (terminal only)..."):
    print("OK")

spf.table(generate_df_2(100))

# -- BREAK --
if input("Press ENTER to see table result (mode aware)"):
    print("OK")


# Return or print table based on mode
def get_result():
    result = generate_df_1(10)
    return spf.table.result(result)


get_result()
