import streamlit as st
import requests
import urllib.parse
import time

# ── Config ──────────────────────────────────────────────────────
PAYOUT_ADDRESS   = "0x0f64c014e50c53828d3fe9117b83b2794f5906e3"
WALLET_API       = "https://api.card2crypto.org/control/wallet.php"
PAYMENT_PAGE     = "https://pay.card2crypto.org/process-payment.php"
HOSTED_PAGE      = "https://pay.card2crypto.org/pay.php"

# (display_name, api_key, accepted_currencies, description)
PROVIDERS = [
    ("🌐 Auto-select (best for my region)", "auto",        ["USD","EUR","GBP","CAD","AUD","INR"], "Card2Crypto picks the best provider for your location automatically."),
    ("🌙 MoonPay",                          "moonpay",     ["USD","EUR","GBP","CAD","AUD"],        "Popular global on-ramp. Visa, Mastercard & Apple Pay."),
    ("🏦 Banxa",                            "banxa",       ["USD","EUR","GBP","CAD","AUD"],        "Bank transfers + cards. Available in 100+ countries."),
    ("⚡ Transak",                          "transak",     ["USD","EUR","GBP","CAD","AUD"],        "Cards & bank transfers. Wide global coverage."),
    ("💳 Stripe",                           "stripe",      ["USD"],                                "Familiar card checkout. USD only."),
    ("🔵 Coinbase",                         "coinbase",    ["USD","EUR","GBP"],                    "Coinbase Pay — fast for existing Coinbase users."),
    ("🟣 Revolut",                          "revolut",     ["USD","EUR","GBP"],                    "Pay via your Revolut account."),
    ("🌿 Ramp Network",                     "rampnetwork", ["USD"],                                "Cards & bank transfers. USD only."),
    ("🏧 Simplex",                          "simplex",     ["USD","EUR","GBP"],                    "Credit/debit cards, no account required."),
    ("🔶 Alchemy Pay",                      "alchemypay",  ["USD","EUR","GBP"],                    "Cards + 300+ local payment methods."),
    ("🦅 Robinhood",                        "robinhood",   ["USD"],                                "Robinhood Connect. USD only."),
    ("🔁 Transfi",                          "transfi",     ["USD"],                                "Global card payments. USD only."),
    ("🌊 Topper",                           "topper",      ["USD","EUR","GBP"],                    "Fast card checkout by Worldpay."),
    ("🐟 Sardine",                          "sardine",     ["USD","EUR","GBP"],                    "Bank transfers & cards with fraud protection."),
    ("🇮🇳 UPI",                             "upi",         ["INR"],                                "India's UPI instant bank transfer. INR only."),
    ("🍁 Interac",                          "interac",     ["CAD"],                                "Canadian Interac e-Transfer. CAD only."),
    ("🌍 Utorg",                            "utorg",       ["USD","EUR","GBP"],                    "Cards. Focus on emerging markets."),
    ("🌐 Unlimit",                          "unlimit",     ["USD","EUR","GBP"],                    "Global card payments provider."),
    ("🟡 Bitnovo",                          "bitnovo",     ["USD","EUR"],                          "Cards & vouchers. Strong in Europe."),
    ("✨ Particle",                         "particle",    ["USD","EUR","GBP"],                    "Web3 social login + card checkout."),
]

CURRENCY_OPTIONS = ["USD", "EUR", "GBP", "CAD", "AUD", "INR"]
# ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Donate", page_icon="💜", layout="centered")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .stApp {
    background: #0a0a0f;
    background-image:
      linear-gradient(rgba(124,106,247,.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(124,106,247,.04) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 3rem; max-width: 560px; }

  .hero { text-align: center; margin-bottom: 2rem; }
  .badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(124,106,247,.12); border: 1px solid rgba(124,106,247,.3);
    color: #7c6af7; font-family: 'Syne', sans-serif;
    font-size: .7rem; font-weight: 700; letter-spacing: .12em;
    text-transform: uppercase; padding: 6px 14px; border-radius: 100px;
    margin-bottom: 20px;
  }
  .hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3rem); font-weight: 800;
    line-height: 1.1; letter-spacing: -.02em; color: #e8e8f0; margin-bottom: 12px;
  }
  .hero h1 span {
    background: linear-gradient(135deg, #7c6af7 0%, #4fd1c5 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  }
  .hero p { color: #6b6b88; font-size: 1rem; }

  .section-label {
    color: #6b6b88 !important; font-size: .78rem !important; font-weight: 500 !important;
    letter-spacing: .08em !important; text-transform: uppercase !important;
    margin-bottom: .5rem !important; margin-top: 1.2rem !important;
  }

  div[data-testid="column"] .stButton > button {
    background: transparent !important;
    border: 1px solid #1e1e2e !important; border-radius: 10px !important;
    color: #6b6b88 !important; font-family: 'Syne', sans-serif !important;
    font-size: .95rem !important; font-weight: 600 !important;
    padding: 10px 0 !important; width: 100% !important;
  }
  div[data-testid="column"] .stButton > button:hover {
    border-color: #7c6af7 !important;
    background: rgba(124,106,247,.1) !important; color: #e8e8f0 !important;
  }

  .stNumberInput > div > div > input,
  .stTextInput  > div > div > input {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid #1e1e2e !important; border-radius: 10px !important;
    color: #e8e8f0 !important; font-family: 'DM Sans', sans-serif !important;
  }
  .stNumberInput > div > div > input:focus,
  .stTextInput  > div > div > input:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,.15) !important;
  }
  label, .stNumberInput label, .stTextInput label,
  .stSelectbox label { color: #6b6b88 !important; font-size: .8rem !important;
    font-weight: 500 !important; letter-spacing: .06em !important;
    text-transform: uppercase !important; }

  .stSelectbox > div > div {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid #1e1e2e !important; border-radius: 10px !important;
    color: #e8e8f0 !important;
  }

  .provider-info {
    background: rgba(124,106,247,.06); border: 1px solid rgba(124,106,247,.2);
    border-radius: 10px; padding: 10px 14px;
    color: #9b94c4; font-size: .85rem; margin-top: .4rem; margin-bottom: .6rem;
  }
  .currencies { display: inline-flex; gap: 6px; margin-top: 6px; flex-wrap: wrap; }
  .currency-tag {
    background: rgba(79,209,197,.08); border: 1px solid rgba(79,209,197,.2);
    color: #4fd1c5; border-radius: 6px; padding: 2px 8px;
    font-size: .72rem; font-weight: 600; font-family: 'Syne', sans-serif; letter-spacing: .05em;
  }
  .currency-tag.active { background: rgba(79,209,197,.22); border-color: #4fd1c5; }
  .warn-tag {
    background: rgba(251,191,36,.08); border: 1px solid rgba(251,191,36,.25);
    color: #fbbf24; border-radius: 8px; padding: 8px 12px;
    font-size: .82rem; margin-top: .5rem;
  }

  .or-divider {
    display: flex; align-items: center; gap: 12px;
    margin: .6rem 0 1rem; color: #6b6b88;
    font-size: .78rem; letter-spacing: .06em; text-transform: uppercase;
  }
  .or-divider::before, .or-divider::after { content: ''; flex: 1; height: 1px; background: #1e1e2e; }

  .stButton > button {
    background: linear-gradient(135deg, #7c6af7 0%, #5a4fe0 100%) !important;
    border: none !important; border-radius: 12px !important;
    color: #fff !important; font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important; font-weight: 700 !important;
    letter-spacing: .04em !important; padding: 14px !important; margin-top: .5rem;
  }
  .stButton > button:hover {
    box-shadow: 0 12px 40px rgba(124,106,247,.4) !important;
    transform: translateY(-2px) !important;
  }

  .trust-strip {
    display: flex; align-items: center; justify-content: center;
    gap: 20px; flex-wrap: wrap; margin-top: 1.2rem;
  }
  .trust-item { display: flex; align-items: center; gap: 6px; color: #6b6b88; font-size: .78rem; }
  .wallet-note {
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(79,209,197,.05); border: 1px solid rgba(79,209,197,.15);
    border-radius: 10px; padding: 12px 14px; margin-top: 1.2rem;
    font-size: .82rem; color: #6b6b88;
  }
  .wallet-note code { color: #4fd1c5; font-size: .75rem; word-break: break-all; }
  .pay-link {
    display: block; text-align: center; margin-top: 1rem; padding: 14px;
    background: linear-gradient(135deg, #7c6af7, #5a4fe0);
    color: #fff !important; border-radius: 12px; font-weight: 700;
    font-family: 'Syne', sans-serif; letter-spacing: .04em;
    text-decoration: none !important; font-size: 1rem;
  }
</style>
""", unsafe_allow_html=True)

# ── Session defaults ─────────────────────────────────────────────
if "amount"   not in st.session_state: st.session_state.amount   = 10.0
if "preset"   not in st.session_state: st.session_state.preset   = 10
if "currency" not in st.session_state: st.session_state.currency = "USD"

# ── Hero ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="badge">⬡ Support our work</div>
  <h1>Make a <span>Donation</span></h1>
  <p>Settled instantly as USDC on Polygon — no middlemen, no delays.</p>
</div>
""", unsafe_allow_html=True)

# ── Amount presets ────────────────────────────────────────────────
st.markdown('<p class="section-label">Choose an amount</p>', unsafe_allow_html=True)
PRESETS = [5, 10, 25, 50]
cols = st.columns(4)
for i, val in enumerate(PRESETS):
    with cols[i]:
        label = f"**${val}**" if st.session_state.preset == val else f"${val}"
        if st.button(label, key=f"p_{val}"):
            st.session_state.preset = val
            st.session_state.amount = float(val)
            st.rerun()

st.markdown('<div class="or-divider">or enter amount</div>', unsafe_allow_html=True)

amount_col, currency_col = st.columns([2, 1])
with amount_col:
    amount = st.number_input(
        "Amount", min_value=1.0, step=1.0,
        value=st.session_state.amount, format="%.2f",
        key="amount_input", label_visibility="collapsed",
    )
with currency_col:
    currency = st.selectbox(
        "Currency", CURRENCY_OPTIONS,
        index=CURRENCY_OPTIONS.index(st.session_state.currency),
        key="currency_select", label_visibility="collapsed",
    )

if amount != st.session_state.amount:
    st.session_state.amount = amount
    if amount not in PRESETS:
        st.session_state.preset = None
if currency != st.session_state.currency:
    st.session_state.currency = currency

# ── Email ─────────────────────────────────────────────────────────
st.markdown('<p class="section-label" style="margin-top:1rem">Your email</p>', unsafe_allow_html=True)
email = st.text_input("Email", placeholder="you@example.com",
                      label_visibility="collapsed", key="email_input")

# ── Provider picker ───────────────────────────────────────────────
st.markdown('<p class="section-label" style="margin-top:1.2rem">Payment provider</p>', unsafe_allow_html=True)

selected_index = st.selectbox(
    "Provider", range(len(PROVIDERS)),
    format_func=lambda i: PROVIDERS[i][0],
    key="provider_select", label_visibility="collapsed",
)

sel            = PROVIDERS[selected_index]
sel_key        = sel[1]
sel_currencies = sel[2]
sel_desc       = sel[3]

currency_tags = "".join(
    f'<span class="currency-tag {"active" if c == currency else ""}">{c}</span>'
    for c in sel_currencies
)
st.markdown(f"""
<div class="provider-info">
  {sel_desc}
  <div class="currencies">{currency_tags}</div>
</div>
""", unsafe_allow_html=True)

currency_mismatch = sel_key != "auto" and currency not in sel_currencies
if currency_mismatch:
    st.markdown(f"""
    <div class="warn-tag">
      ⚠️ <strong>{sel[0]}</strong> doesn't support <strong>{currency}</strong>.
      Switch to {" / ".join(sel_currencies)} or choose a different provider.
    </div>
    """, unsafe_allow_html=True)

# ── Donate button ─────────────────────────────────────────────────
st.markdown("")
clicked = st.button("💜  Donate Now", use_container_width=True, key="donate_btn")

if clicked:
    if amount < 1:
        st.error("Please enter a donation amount of at least $1.")
    elif not email or "@" not in email or "." not in email.split("@")[-1]:
        st.error("Please enter a valid email address.")
    elif currency_mismatch:
        st.error(f"{sel[0]} doesn't support {currency}. Please fix the currency or pick another provider.")
    else:
        with st.spinner("Preparing your payment…"):
            try:
                unique_id  = int(time.time() * 1000)
                callback   = f"https://example.com/callback?donation={unique_id}"
                wallet_url = (
                    f"{WALLET_API}"
                    f"?address={PAYOUT_ADDRESS}"
                    f"&callback={urllib.parse.quote(callback, safe='')}"
                )
                resp = requests.get(wallet_url, timeout=10)
                resp.raise_for_status()
                encrypted = resp.json().get("address_in")

                if not encrypted:
                    st.error("Could not get a payment address. Please try again.")
                else:
                    if sel_key == "auto":
                        pay_url = (
                            f"{HOSTED_PAGE}"
                            f"?address={encrypted}"
                            f"&amount={urllib.parse.quote(f'{amount:.2f}')}"
                            f"&email={urllib.parse.quote(email)}"
                            f"&currency={currency}"
                            f"&domain=pay.card2crypto.org"
                        )
                    else:
                        pay_url = (
                            f"{PAYMENT_PAGE}"
                            f"?address={encrypted}"
                            f"&amount={urllib.parse.quote(f'{amount:.2f}')}"
                            f"&provider={sel_key}"
                            f"&email={urllib.parse.quote(email)}"
                            f"&currency={currency}"
                        )

                    st.success("Payment ready! Click below to complete your donation.")
                    st.markdown(
                        f'<a href="{pay_url}" target="_blank" class="pay-link">'
                        f'→ Complete Payment via {sel[0]}</a>',
                        unsafe_allow_html=True,
                    )

            except requests.exceptions.Timeout:
                st.error("The payment gateway timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ── Footer ────────────────────────────────────────────────────────
st.markdown("""
<div class="trust-strip">
  <div class="trust-item">🔒 Secure &amp; Encrypted</div>
  <div class="trust-item">⚡ Instant Settlement</div>
  <div class="trust-item">💳 19 Payment Providers</div>
</div>
<div class="wallet-note">
  ℹ️&nbsp; All payments settle as <strong>USDC on Polygon</strong> to:<br/>
  <code>0x0f64c014e50c53828d3fe9117b83b2794f5906e3</code>
</div>
""", unsafe_allow_html=True)
