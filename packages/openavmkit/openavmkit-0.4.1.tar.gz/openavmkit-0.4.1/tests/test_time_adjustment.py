import pandas as pd

from openavmkit.data import get_hydrated_sales_from_sup, SalesUniversePair
from openavmkit.synthetic.basic import generate_basic
from openavmkit.time_adjustment import _interpolate_missing_periods, calculate_time_adjustment, apply_time_adjustment
from openavmkit.utilities.assertions import lists_are_equal


def test_interpolate_missing_periods_days():
  print("")
  data = {
    "period": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "21", "30", "41"],
    "median": [ 1 ,  2,   3,   4,   5,   6,   7,   8,   9,   10,   21,   30,   41]
  }
  df_median = pd.DataFrame(data)
  df_median = df_median.groupby("period")["median"].agg(["count","median"])
  periods_actual = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "21", "30", "41"]
  periods_expected = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
    "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41"
  ]
  results = _interpolate_missing_periods(
    periods_expected,
    periods_actual,
    df_median
  ).tolist()
  expected = [
    1., 2., 3., 4., 5., 6., 7., 8., 9., 10.,
    11., 12., 13., 14., 15., 16., 17., 18., 19., 20.,
    21., 22., 23., 24., 25., 26., 27., 28., 29., 30.,
    31., 32., 33., 34., 35., 36., 37., 38., 39., 40.,
    41.
  ]
  assert(lists_are_equal(expected, results))


def test_interpolate_missing_periods():
  print("")
  data = {
    "period": ["2014", "2016", "2019", "2020", "2021", "2022", "2024"],
    "median": [     1,      3,      6,      7,      8,      9,     11]
  }
  df_median = pd.DataFrame(data)
  df_median = df_median.groupby("period")["median"].agg(["count","median"])
  periods_actual = ["2014", "2015", "2016", "2019", "2020", "2021", "2022", "2023", "2024"]
  periods_expected = ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]
  results = _interpolate_missing_periods(
    periods_expected,
    periods_actual,
    df_median
  ).tolist()
  expected = [1., 1., 2., 3., 4., 5., 6., 7., 8., 9., 10., 11., 11.]
  assert(lists_are_equal(expected, results))


def test_time_adjustment():
  print("")
  sd = generate_basic(100)

  sup = SalesUniversePair(sd.df_sales, sd.df_universe)
  df = get_hydrated_sales_from_sup(sup)

  df.loc[df["sale_year_quarter"].eq("2024-Q3"), "sale_price_per_impr_sqft"] = None

  # TODO: replace with proper sales subset function
  df = df[df["sale_price"].gt(0) & df["valid_sale"].ge(1)]

  df_time_m = calculate_time_adjustment(df, settings={}, period="M")
  df_time_q = calculate_time_adjustment(df, settings={}, period="Q")
  df_time_y = calculate_time_adjustment(df, settings={}, period="Y")

  time_land_mult = sd.time_land_mult.copy()

  time_land_mult["value"] = time_land_mult["value"] / time_land_mult["value"].iloc[0]

  df_norm = df.copy()
  df_norm = df_norm[df_norm["sale_price_per_impr_sqft"].gt(0)]
  df_norm["period"] = pd.to_datetime(df_norm["sale_year_quarter"])
  first_period = df_norm["period"].min()
  df_norm["sale_price_per_impr_sqft"] = df_norm["sale_price_per_impr_sqft"] / df_norm[df_norm["period"].eq(first_period)]["sale_price_per_impr_sqft"].median()

  # plt.plot(df_time_m["period"], df_time_m["value"])
  # plt.plot(df_time_q["period"], df_time_q["value"])
  # plt.plot(df_time_y["period"], df_time_y["value"])
  # plt.plot(time_land_mult["period"], time_land_mult["value"])
  #
  # #scatterplot df norm:
  # plt.scatter(df_norm["period"], df_norm["sale_price_per_impr_sqft"], color="gray", s=1)
  #
  # plt.show()


def test_apply_time_adjustment():
  print("")
  sd = generate_basic(100)

  sup = SalesUniversePair(sd.df_sales, sd.df_universe)
  df = get_hydrated_sales_from_sup(sup)

  # TODO: replace with proper sales subset function
  df = df[df["sale_price"].gt(0) & df["valid_sale"].ge(1)]

  for period, color, color2 in [("M","red", "pink"), ("Q","blue", "skyblue"), ("Y","black", "lightgray")]:
    df = apply_time_adjustment(df, settings={}, period=period, verbose=True)

    df_median = df.groupby("sale_year_month")["sale_price_time_adj_per_impr_sqft"].agg(["count", "median"])
    df_median["period"] = pd.to_datetime(df_median.index)

    # plt.plot(df_median["period"], df_median["median"], color=color)
    # plt.scatter(df["sale_date"], df["sale_price_per_impr_sqft"], s=1, color=color2)
    # plt.scatter(df["sale_date"], df["sale_price_time_adj_per_impr_sqft"], s=1, color=color2)

  # plt.show()
