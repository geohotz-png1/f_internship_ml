import streamlit as st
import google.generativeai as genai
import os

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="SwiftCart Support",
    page_icon="logo.png",
    layout="wide"
)

# --- Custom CSS for Layout and Style ---
st.markdown("""
<style>
    /* Main app background */
    .stApp {
        background-image: url("https://plus.unsplash.com/premium_photo-1674582717470-8e0b39f643e2?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
    }

    /* The main glass container */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.16);
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        -webkit-backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 2rem;
    }

    /* Make text inside the container dark for readability */
    div[data-testid="stVerticalBlockBorderWrapper"] * {
        color: #1D1D1F;
    }
    
    /* Remove default Streamlit border */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none;
    }

    /* FIX FOR CHAT INPUT TEXT COLOR */
    div[data-testid="stChatInput"] input {
        color: #FFFFFF !important;
    }
    div[data-testid="stChatInput"] input::placeholder {
        color: #CCCCCC !important;
    }

    /* Hide Streamlit header/footer */
    header, footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- API Key Configuration in Sidebar ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("Enter your Google Gemini API Key below.")
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
        st.success("API key loaded from environment.", icon="✅")
    except KeyError:
        api_key = st.text_input("Google API Key", type="password", label_visibility="collapsed")
        if not api_key:
            st.warning("Please enter your API key to start the chat.", icon="⚠️")
            st.stop()
        st.success("API key accepted.", icon="✅")

# --- Centered Layout ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # --- Main Chat Container ---
    with st.container(border=True):
        # --- 1. Header (Fixed at the top) ---
        logo_col, title_col = st.columns([1, 4])
        with logo_col:
            st.image("logo.png", width=80) 
        with title_col:
            st.title("SwiftCart Support")
            st.caption("Powered by AI")
        
        st.divider()

        # --- 2. Scrollable Chat History Area ---
        chat_history_container = st.container(height=400)
        with chat_history_container:
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # --- 3. Chat Input (Fixed at the bottom of the container) ---
        if prompt := st.chat_input("Ask about your order, returns, or more..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

# --- Response Generation Logic ---
try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    st.error(f"Error configuring Google AI: {e}", icon="🔴")
    st.stop()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_user_message = st.session_state.messages[-1]["content"]
    try:
        # This is the updated, more detailed prompt
        full_prompt = f"""
        You are a helpful and friendly customer support assistant for a fictional online store called "SwiftCart".
        Your name is Gem. You are designed to provide quick and accurate information to customers.
        Your goal is to answer user questions based ONLY on the information provided below.
        If a user asks a question not covered in the information, politely state that you cannot answer and suggest they contact a human agent at support@swiftcart.com or call +91-987-654-3210. Do not invent answers.

        *** Current Context ***
        - The current date is Tuesday, July 8, 2025.
        - Our business hours are 9 AM to 6 PM IST, Monday to Friday.

        *** FAQ Information ***

        **1. Orders & Returns:**
        - **Order Tracking:** Customers can track their order on our website: swiftcart.com/tracking. They will need their order number.
        - **Return Policy:** We have a 30-day return policy for items in their original, unused condition with all tags attached. To start a return, visit swiftcart.com/returns.
        - **Canceling an Order:** Orders can be canceled within 2 hours of placement from the 'My Orders' section. After that, the order is processed and cannot be canceled.
        - **Changing an Order:** Unfortunately, we cannot modify an order (like changing size or color) once it has been placed. The customer would need to cancel and re-order within the 2-hour window.
        - **Damaged Items:** If an item arrives damaged, please contact us within 48 hours with photos of the damage at support@swiftcart.com.

        **2. Shipping & Delivery:**
        - **Shipping Locations:** We currently ship to all major cities and towns within India. We do not offer international shipping.
        - **Shipping Costs:** Standard shipping is free for all orders over ₹499. For orders below this amount, a flat fee of ₹50 is charged.
        - **Delivery Time:** Standard shipping typically takes 3-5 business days. Express shipping (available in metro cities) takes 1-2 business days for an additional fee of ₹100.

        **3. Payments & Pricing:**
        - **Payment Methods:** We accept all major credit cards (Visa, MasterCard), debit cards, UPI (GPay, PhonePe, etc.), and Net Banking.
        - **Cash on Delivery (COD):** We do not offer a Cash on Delivery option at this time.
        - **Discounts:** Discount codes can be applied at checkout. Only one code can be used per order.

        **4. Products & Warranty:**
        - **Warranty:** Electronics come with a 1-year manufacturer's warranty. For claims, please contact the manufacturer directly with your SwiftCart invoice.
        - **Out of Stock:** If an item is out of stock, customers can sign up on the product page to be notified via email when it is available again.

        **5. About SwiftCart:**
        - **Contact Phone:** +91-987-654-3210.
        - **Email Support:** support@swiftcart.com
        - **Our Mission:** SwiftCart is an Indian e-commerce platform based in Kochi, Kerala, dedicated to providing quality products with fast and reliable delivery.

        *** Conversation History ***
        {''.join([f'{m["role"]}: {m["content"]}\\n' for m in st.session_state.messages[:-1]])}
        
        *** Current Question ***
        user: {last_user_message}
        assistant:
        """
        
        with st.spinner("Thinking..."):
            response = model.generate_content(full_prompt)
            assistant_response = response.text
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.rerun()

    except Exception as e:
        st.error(f"An error occurred: {e}", icon="🔴")