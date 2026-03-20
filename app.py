import streamlit as st
import requests
import urllib.parse
import time

# ── Config ─────────────────────────────────────────────────────
PAYOUT_ADDRESS = "0x0f64c014e50c53828d3fe9117b83b2794f5906e3"
WALLET_API     = "https://api.card2crypto.org/control/wallet.php"
PAYMENT_PAGE   = "https://pay.card2crypto.org/pay.php"
# ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Donate",
    page_icon="💜",
    layout="centered",
)

# ── Styling ─────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Dark background */
  .stApp {
    background: #0a0a0f;
    background-image:
      linear-gradient(rgba(124,106,247,.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(124,106,247,.04) 1px, transparent 1px);
    background-size: 40px 40px;
  }

  /* Top glow */
  .stApp::before {
    content: '';
    position: fixed;
    top: -30vh; left: 50%;
    transform: translateX(-50%);
    width: 80vw; height: 80vh;
    background: radial-gradient(ellipse at 50% 0%, rgba(124,106,247,.15) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  /* Hide default Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 3rem; max-width: 520px; }

  /* ── Hero ── */
  .hero { text-align: center; margin-bottom: 2rem; }
  .badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(124,106,247,.12);
    border: 1px solid rgba(124,106,247,.3);
    color: #7c6af7;
    font-family: 'Syne', sans-serif;
    font-size: .7rem; font-weight: 700;
    letter-spacing: .12em; text-transform: uppercase;
    padding: 6px 14px; border-radius: 100px;
    margin-bottom: 20px;
  }
  .badge-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #7c6af7;
    animation: pulse 2s ease infinite;
    display: inline-block;
  }
  .hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 800; line-height: 1.1;
    letter-spacing: -.02em; color: #e8e8f0;
    margin-bottom: 12px;
  }
  .hero h1 span {
    background: linear-gradient(135deg, #7c6af7 0%, #4fd1c5 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .hero p { color: #6b6b88; font-size: 1rem; }

  /* ── Card shell ── */
  .donate-card {
    background: #111118;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    padding: 32px 28px;
    box-shadow: 0 24px 80px rgba(0,0,0,.5);
  }

  /* ── Preset buttons ── */
  .preset-row { display: flex; gap: 10px; margin-bottom: 1.5rem; }
  .preset-btn {
    flex: 1; background: transparent;
    border: 1px solid #1e1e2e; border-radius: 10px;
    color: #6b6b88;
    font-family: 'Syne', sans-serif; font-size: .95rem; font-weight: 600;
    padding: 10px 0; cursor: pointer;
    transition: all .2s; text-align: center;
  }
  .preset-btn:hover, .preset-btn.active {
    border-color: #7c6af7;
    background: rgba(124,106,247,.12);
    color: #e8e8f0;
  }

  /* ── Inputs ── */
  .stNumberInput > div > div > input,
  .stTextInput > div > div > input {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
    color: #e8e8f0 !important;
    font-family: 'DM Sans', sans-serif !important;
  }
  .stNumberInput > div > div > input:focus,
  .stTextInput > div > div > input:focus {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,.15) !important;
  }
  label, .stNumberInput label, .stTextInput label {
    color: #6b6b88 !important;
    font-size: .8rem !important;
    font-weight: 500 !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
    font-family: 'DM Sans', sans-serif !important;
  }

  /* ── Donate button ── */
  .stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #7c6af7 0%, #5a4fe0 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important; font-weight: 700 !important;
    letter-spacing: .04em !important;
    padding: 14px !important;
    transition: transform .15s, box-shadow .15s !important;
    margin-top: .5rem;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px rgba(124,106,247,.4) !important;
  }

  /* ── Trust strip ── */
  .trust-strip {
    display: flex; align-items: center; justify-content: center;
    gap: 20px; flex-wrap: wrap;
    margin-top: 1.2rem;
  }
  .trust-item {
    display: flex; align-items: center; gap: 6px;
    color: #6b6b88; font-size: .78rem;
  }

  /* ── Wallet note ── */
  .wallet-note {
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(79,209,197,.05);
    border: 1px solid rgba(79,209,197,.15);
    border-radius: 10px; padding: 12px 14px;
    margin-top: 1.2rem; font-size: .82rem; color: #6b6b88;
  }
  .wallet-note code { color: #4fd1c5; font-size: .75rem; word-break: break-all; }

  /* ── Divider ── */
  .or-divider {
    display: flex; align-items: center; gap: 12px;
    margin: .5rem 0 1rem; color: #6b6b88;
    font-size: .78rem; letter-spacing: .06em; text-transform: uppercase;
  }
  .or-divider::before, .or-divider::after {
    content: ''; flex: 1; height: 1px; background: #1e1e2e;
  }

  /* ── Alerts ── */
  .stAlert { border-radius: 10px !important; }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: .5; transform: scale(.8); }
  }
</style>
""", unsafe_allow_html=True)


# ── Hero ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="badge"><span class="badge-dot"></span> Support our work</div>
  <h1>Make a <span>Donation</span></h1>
  <p>Your contribution is received instantly as USDC on Polygon —<br>no middlemen, no delays.</p>
</div>
""", unsafe_allow_html=True)


# ── Preset buttons (HTML trick via component) ─────────────────────
st.markdown('<div class="donate-card">', unsafe_allow_html=True)

PRESETS = [5, 10, 25, 50]

if "amount" not in st.session_state:
    st.session_state.amount = 10.0
if "preset" not in st.session_state:
    st.session_state.preset = 10

st.markdown("**Choose an amount**", unsafe_allow_html=False)

cols = st.columns(4)
for i, val in enumerate(PRESETS):
    with cols[i]:
        label = f"**${val}**" if st.session_state.preset == val else f"${val}"
        if st.button(label, key=f"preset_{val}"):
            st.session_state.preset = val
            st.session_state.amount = float(val)
            st.rerun()

st.markdown('<div class="or-divider">or enter amount</div>', unsafe_allow_html=True)

amount = st.number_input(
    "Donation Amount (USD)",
    min_value=1.0,
    step=1.0,
    value=st.session_state.amount,
    format="%.2f",
    key="amount_input",
)

# Sync manual input back to state (deselects preset if different)
if amount != st.session_state.amount:
    st.session_state.amount = amount
    if amount not in PRESETS:
        st.session_state.preset = None

email = st.text_input(
    "Your Email (for payment receipt)",
    placeholder="you@example.com",
    key="email_input",
)

# ── Donate button ──────────────────────────────────────────────────
clicked = st.button("💜  Donate Now", use_container_width=True)

if clicked:
    # Validate
    if amount < 1:
        st.error("Please enter a donation amount of at least $1.")
    elif not email or "@" not in email or "." not in email.split("@")[-1]:
        st.error("Please enter a valid email address.")
    else:
        with st.spinner("Preparing your payment…"):
            try:
                unique_id   = int(time.time() * 1000)
                callback    = f"https://example.com/callback?donation={unique_id}"
                wallet_url  = (
                    f"{WALLET_API}"
                    f"?address={PAYOUT_ADDRESS}"
                    f"&callback={urllib.parse.quote(callback, safe='')}"
                )

                resp = requests.get(wallet_url, timeout=10)
                resp.raise_for_status()
                data = resp.json()

                encrypted = data.get("address_in")
                if not encrypted:
                    st.error("Could not get a payment address. Please try again.")
                else:
                    # Build redirect URL — address is already URL-encoded, don't re-encode it
                    pay_url = (
                        f"{PAYMENT_PAGE}"
                        f"?address={encrypted}"
                        f"&amount={urllib.parse.quote(f'{amount:.2f}')}"
                        f"&email={urllib.parse.quote(email)}"
                        f"&currency=USD"
                        f"&domain=pay.card2crypto.org"
                    )

                    st.success("Payment ready! Click the button below to complete your donation.")
                    st.markdown(
                        f'<a href="{pay_url}" target="_blank" style="'
                        'display:block;text-align:center;margin-top:1rem;padding:14px;'
                        'background:linear-gradient(135deg,#7c6af7,#5a4fe0);'
                        'color:#fff;border-radius:12px;font-weight:700;'
                        'font-family:Syne,sans-serif;letter-spacing:.04em;'
                        'text-decoration:none;font-size:1rem;">'
                        '→ Complete Payment</a>',
                        unsafe_allow_html=True,
                    )

            except requests.exceptions.Timeout:
                st.error("The payment gateway timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"Network error: {e}")
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ── Trust strip ────────────────────────────────────────────────────
st.markdown("""
<div class="trust-strip">
  <div class="trust-item">🔒 Secure &amp; Encrypted</div>
  <div class="trust-item">⚡ Instant Settlement</div>
  <div class="trust-item">💳 Card / Bank Transfer</div>
</div>

<div class="wallet-note">
  ℹ️&nbsp; Payments are settled as <strong>USDC on Polygon</strong> to:<br/>
  <code>0x0f64c014e50c53828d3fe9117b83b2794f5906e3</code>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close .donate-card
