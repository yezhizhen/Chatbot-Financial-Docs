import streamlit as st


def hide_footer():
    # #MainMenu {visibility: hidden;}
    hide_streamlit_style = """
                <style>
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def background(file_name):
    import base64

    @st.cache_data
    def get_base64_of_bin_file(bin_file):
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def set_png_as_page_bg(png_file):
        bin_str = get_base64_of_bin_file(png_file)
        page_bg_img = (
            """
        <style>
        .stApp  {
        background-image: url("data:image/png;base64,%s");
        background-size: auto;
        }
        </style>
        """
            % bin_str
        )

        st.markdown(page_bg_img, unsafe_allow_html=True)
        return

    set_png_as_page_bg(file_name)


# not used yet
def background_link():
    from streamlit.elements import image

    url = image.image_to_url(
        "Front End OCBC/dots cover.jpg",
        width=-1,  # Always use full width for favicons
        clamp=False,
        channels="RGB",
        output_format="auto",
        image_id="favicon",
    )
    print(url)
    page_bg_img = (
        """
    <style>
    body {
    background-image: url("%s");
    background-size: cover;
    }
    </style>
    """
        % url
    )

    st.markdown(page_bg_img, unsafe_allow_html=True)


def authenticate(cre_path, msg):
    import streamlit_authenticator as stauth
    import yaml
    from yaml.loader import SafeLoader

    with open(cre_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            config["preauthorized"],
        )
        authenticator.login(msg, "main")

        if st.session_state["authentication_status"]:
            authenticator.logout("Logout", "sidebar", key="unique_logout_key")
            if "logging" not in st.session_state:
                st.toast(f'Welcome *{st.session_state["name"]}*', icon="✅")
                st.session_state["logging"] = True
        elif st.session_state["authentication_status"] is False:
            st.error("Username/password is incorrect")
        elif st.session_state["authentication_status"] is None:
            st.warning("Please enter your username and password")
            st.session_state.pop("logging", None)
