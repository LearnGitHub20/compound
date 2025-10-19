import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Currency symbols only
# ----------------------------
CURRENCY_SYMBOL = {
    "GBP": "£",
    "INR": "₹",
    "USD": "$"
}

# ----------------------------
# Simulation functions
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

    df["Total Invested"] = invested_amounts
    return df

# ----------------------------
# Streamlit App
# ----------------------------
def main():
	# At the very top of main(), after st.set_page_config()
	st.image("RFin.png", width=150)  # optional logo

# Add the quote
	st.markdown(
    """
    <div style='text-align:center; font-size:18px; color:#0d47a1; font-style:italic; margin-bottom:20px;'>
    "Compound interest is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it."
    </div>
    """,
    unsafe_allow_html=True
)

# App title
	st.title("💷 Investment Growth Simulator")
	st.set_page_config(page_title="💷 Investment Growth Simulator", layout="wide")
	st.title("💷 Investment Growth Simulator")
	# Sidebar inputs
	st.sidebar.header("Enter Your Investment Details 🎯")
	current_age = st.sidebar.number_input("Current Age", min_value=1, max_value=120, value=25)
	monthly_investment = st.sidebar.number_input("Initial Monthly Investment", min_value=0.0, value=500.0, step=50.0)
	end_age = st.sidebar.number_input("Invest Until Age", min_value=current_age + 1, max_value=120, value=60)
	compounding_end_age = st.sidebar.number_input("Compound Until Age (optional)", min_value=current_age + 1, max_value=120, value=end_age)
	
	st.sidebar.markdown("---")
	st.sidebar.subheader("Investment Increases 📈")
	increases = []
	num_increases = st.sidebar.number_input("Number of Increases", 0, 10, 0)

    for i in range(num_increases):
		after_years = st.sidebar.number_input(f"Increase {i+1}: After how many years?", 0, end_age - current_age - 1, 5, key=f"iy_{i}")
        new_amt = st.sidebar.number_input(f"Increase {i+1}: New Monthly Amount", 0.0, 1_000_000.0, 700.0, step=50.0, key=f"ia_{i}")
        increases.append((after_years, new_amt))

    # ----------------------------
    # Calculate button
    # ----------------------------
    calculate = st.sidebar.button("💡 Calculate Growth")

    # Currency selector
    currency = st.sidebar.selectbox("Select Currency", ["GBP", "INR", "USD"], index=0)
    symbol = CURRENCY_SYMBOL[currency]

    if calculate:
        rates = [8, 10, 12, 15]
        results, total_years = simulate_investment(
            current_age, monthly_investment, end_age, increases, rates, compounding_end_age
        )

        df = build_yearly_df(total_years, results, increases, monthly_investment, rates, current_age)

        # Apply currency symbol only
        for r in rates:
            df[f"{r}% Return"] = df[f"{r}% Return"].apply(lambda x: f"{symbol}{x:,}")
        df["Total Invested"] = df["Total Invested"].apply(lambda x: f"{symbol}{x:,}")

        st.subheader("📊 Year-by-Year Breakdown with Age")
        st.dataframe(df, use_container_width=True)

        st.subheader("💰 Summary Table")
        summary_rows = []
        for r in rates:
            final_val = results[r][0][-1] if results[r][0] else 0
            invested_total = results[r][1]
            summary_rows.append({
                "Rate (%)": f"{r}%",
                "Final Value": f"{symbol}{int(final_val):,}",
                "Total Invested": f"{symbol}{int(invested_total):,}"
            })
        st.table(pd.DataFrame(summary_rows))

        # ----------------------------
        # Growth chart
        # ----------------------------
        st.subheader("📈 Growth Chart")
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#1976d2', '#43a047', '#fbc02d', '#e53935']

        for i, r in enumerate(rates):
            y = [val for val in results[r][0]]
            ax.plot(df["Year"], y, label=f"{r}% return", linewidth=2.5, color=colors[i])
            ax.text(df["Year"].iloc[-1], y[-1], f"{symbol}{int(y[-1]):,}", fontsize=9, color=colors[i], verticalalignment='bottom')

        # Total invested line
        total_invested_line = [x for x in [results[rates[0]][1] / rates[0] * rates[0] for _ in range(total_years)]]
        total_invested_line = [x for x in df["Total Invested"].apply(lambda v: int(v.replace(symbol, "").replace(",", "")))]
        ax.plot(df["Year"], total_invested_line, linestyle='--', color='black', linewidth=2, label=f"Total Invested ({symbol})")

        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel(f"Portfolio Value ({symbol})", fontsize=12)
        ax.set_title(f"Investment Growth Over Time ({symbol})", fontsize=14, fontweight='bold', color="#0d47a1")
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()
        st.pyplot(fig)

        st.success(f"✨ Values displayed in {currency} only; amounts are unchanged, only the symbol updates.")
    else:
        st.info("👈 Enter your details and click **Calculate Growth** to see results.")

if __name__ == "__main__":
    main()







