import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


# ----------------------------
# Helper functions
# ----------------------------
def simulate_investment(current_age, monthly_investment, end_age, increases, rates, compounding_end_age=None):
    increases = sorted(increases or [], key=lambda x: x[0])
    total_years = end_age - current_age
    compounding_years = (compounding_end_age or end_age) - current_age
    months = total_years * 12

    results = {}
    increase_map = {int(y * 12): amt for y, amt in increases}

    for rate in rates:
        r = rate / 100 / 12
        balance = 0.0
        current_contribution = monthly_investment
        yearly_values = []
        invested = 0.0

        for m in range(1, months + 1):
            if m in increase_map:
                current_contribution = increase_map[m]

            balance += current_contribution
            invested += current_contribution

            if m <= compounding_years * 12:
                balance *= (1 + r)

            if m % 12 == 0:
                yearly_values.append(balance)

        results[rate] = (yearly_values, invested)

    return results, total_years


def build_yearly_df(total_years, results, increases, monthly_investment, rates, starting_age):
    years = list(range(1, total_years + 1))
    df = pd.DataFrame({"Year": years, "Age": [starting_age + y for y in years]})

    for rate in rates:
        vals = results[rate][0]
        df[f"{rate}% Return"] = [int(round(v, 0)) for v in vals]

    # Total invested
    incs_sorted = sorted(increases or [], key=lambda x: x[0])
    invested_amounts = []
    current_amt = monthly_investment
    total_invested = 0.0
    next_inc = 0
    for y in range(1, total_years + 1):
        if next_inc < len(incs_sorted) and y > incs_sorted[next_inc][0]:
            current_amt = incs_sorted[next_inc][1]
            next_inc += 1
        total_invested += current_amt * 12
        invested_amounts.append(int(total_invested))

    df["Total Invested (£)"] = invested_amounts
    return df


# ----------------------------
# Streamlit UI
# ----------------------------
def main():
	st.image("RFin logo.png", width=150)  # adjust width as needed
    st.set_page_config(page_title="💷 Compound Interst Growth Simulator", layout="wide")

    # Add colorful CSS
    st.markdown("""
        <style>
        .main {
            background: linear-gradient(to bottom right, #F0F9FF, #CBEBFF);
        }
        .stApp {
            background-color: #e3f2fd;
        }
        h1 {
            color: #1565c0 !important;
            text-align: center;
        }
        h2, h3, h4 {
            color: #0d47a1 !important;
        }
        div[data-testid="stSidebar"] {
            background: linear-gradient(to bottom, #90caf9, #e3f2fd);
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("💷 Compound Investment Growth Simulator")

    st.sidebar.header("Enter Your Investment Details 🎯")
    current_age = st.sidebar.number_input("Current Age", min_value=1, max_value=120, value=25)
    monthly_investment = st.sidebar.number_input("Initial Monthly Investment (£)", min_value=0.0, value=500.0, step=50.0)
    end_age = st.sidebar.number_input("Invest Until Age", min_value=current_age + 1, max_value=120, value=60)
    compounding_end_age = st.sidebar.number_input("Compound Until Age (optional)", min_value=current_age + 1, max_value=120, value=end_age)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Investment Increases 📈")
    increases = []
    num_increases = st.sidebar.number_input("Number of Increases", 0, 10, 0)

    for i in range(num_increases):
        after_years = st.sidebar.number_input(f"Increase {i+1}: After how many years?", 0, end_age - current_age - 1, 5, key=f"iy_{i}")
        new_amt = st.sidebar.number_input(f"Increase {i+1}: New Monthly Amount (£)", 0.0, 1_000_000.0, 700.0, step=50.0, key=f"ia_{i}")
        increases.append((after_years, new_amt))

    calculate = st.sidebar.button("💡 Calculate Growth")

    if calculate:
        rates = [8, 10, 12, 15]
        results, total_years = simulate_investment(
            current_age, monthly_investment, end_age, increases, rates, compounding_end_age
        )

        df = build_yearly_df(total_years, results, increases, monthly_investment, rates, current_age)

        st.subheader("📊 Year-by-Year Breakdown with Age")
        st.dataframe(df.style.highlight_max(axis=0, color="#bbdefb"), use_container_width=True)

        st.subheader("💰 Summary Table")
        summary_rows = []
        for rate in rates:
            final = int(round(results[rate][0][-1])) if results[rate][0] else 0
            invested_total = int(round(results[rate][1]))
            summary_rows.append({
                "Rate (%)": f"{rate}%",
                "Final Value (£)": f"£{final:,}",
                "Total Invested (£)": f"£{invested_total:,}"
            })

        st.table(pd.DataFrame(summary_rows))

        # --- Chart ---
        st.subheader("📈 Growth Chart")
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['#1976d2', '#43a047', '#fbc02d', '#e53935']
        for i, rate in enumerate(rates):
            y = df[f"{rate}% Return"]
            ax.plot(df["Year"], y, label=f"{rate}% return", linewidth=2.5, color=colors[i])
            # Annotate final value
            ax.text(
                df["Year"].iloc[-1],
                y.iloc[-1],
                f" £{y.iloc[-1]:,}",
                fontsize=9,
                color=colors[i],
                verticalalignment='bottom'
            )

        ax.plot(df["Year"], df["Total Invested (£)"], linestyle='--', color='black', linewidth=2, label="Total Invested (£)")

        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Portfolio Value (£)", fontsize=12)
        ax.set_title("Investment Growth Over Time", fontsize=14, fontweight='bold', color="#0d47a1")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()

        st.pyplot(fig)

        st.success("✨ Each label on the chart shows the final portfolio value for that return rate.")
    else:
        st.info("👈 Enter your details on the left and click **Calculate Growth** to begin!")


if __name__ == "__main__":
    main()
