import pandas as pd
import numpy as np
import streamlit as st


def page2():
    st.title("Second page")
    st.text("this is test page 2.")
    st.text("show dataframe.")

    df = pd.DataFrame(
        np.random.randint(1, 100, (20, 10)),
        columns=[f"col_{i}" for i in range(10)],
    )
    st.dataframe(df)
    # st.download_button(
    #     label="download",
    #     data=df.to_csv(index=None).encode("utf-8"),
    #     file_name="dataframe.csv",
    # )


def main():
    pages = {
        "section 1": [
            st.Page("./subpages/chatbot_page.py", title="First page: chatbot", icon="🔥"),
        ],
        "section 2": [
            st.Page(page2, title="Second page: dataframe", icon="🤗"),
        ],
    }

    nav = st.navigation(pages)
    nav.run()


if __name__ == "__main__":
    main()
