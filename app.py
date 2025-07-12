import streamlit as st
import pandas as pd
import os

# Initialize CSVs if not exist
for file in ["users.csv", "swap_requests.csv", "feedback.csv"]:
    if not os.path.exists(file):
        pd.DataFrame().to_csv(file, index=False)

# Load data
def load_csv(file):
    return pd.read_csv(file) if os.path.getsize(file) > 0 else pd.DataFrame()

users_df = load_csv("users.csv")
swaps_df = load_csv("swap_requests.csv")
feedback_df = load_csv("feedback.csv")

st.title("🔁 Skill Swap Platform")

# Tabs
tab = st.sidebar.radio("Menu", ["Register / Profile", "Browse", "Swap Requests", "Feedback", "Admin"])

# ---------------- Register / Profile ----------------
if tab == "Register / Profile":
    st.header("📋 Create or View Your Profile")
    name = st.text_input("Your Name")
    location = st.text_input("Location (optional)")
    offered = st.text_input("Skills Offered (comma-separated)")
    wanted = st.text_input("Skills Wanted (comma-separated)")
    availability = st.multiselect("Availability", ["Weekends", "Evenings", "Weekdays"])
    is_public = st.checkbox("Make Profile Public?", value=True)

    if st.button("Save Profile"):
        new_user = pd.DataFrame([{
            "name": name, "location": location,
            "skills_offered": offered, "skills_wanted": wanted,
            "availability": ",".join(availability), "is_public": is_public
        }])
        users_df = users_df[users_df["name"] != name]  # remove old entry
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv("users.csv", index=False)
        st.success("Profile saved successfully!")

# ---------------- Browse Users ----------------
elif tab == "Browse":
    st.header("🔍 Browse Public Profiles by Skill")
    skill_search = st.text_input("Search skill (e.g., Photoshop)")
    public_profiles = users_df[users_df["is_public"] == True]

    if skill_search:
        results = public_profiles[
            public_profiles["skills_offered"].str.contains(skill_search, case=False, na=False) |
            public_profiles["skills_wanted"].str.contains(skill_search, case=False, na=False)
        ]
    else:
        results = public_profiles

    for _, row in results.iterrows():
        st.markdown(f"**{row['name']}** - _{row['location']}_")
        st.markdown(f"🎯 **Offers**: {row['skills_offered']} | 🤝 **Wants**: {row['skills_wanted']}")
        st.markdown(f"🕒 **Availability**: {row['availability']}")
        if st.button(f"Request Swap with {row['name']}"):
            sender = st.text_input("Your Name (Confirm)", key=row['name'])
            message = st.text_area("Message", key=row['name']+"msg")
            if st.button("Send Swap Request", key=row['name']+"btn"):
                new_swap = pd.DataFrame([{
                    "from_user": sender, "to_user": row["name"],
                    "message": message, "status": "pending"
                }])
                swaps_df = pd.concat([swaps_df, new_swap], ignore_index=True)
                swaps_df.to_csv("swap_requests.csv", index=False)
                st.success("Swap request sent!")

# ---------------- Swap Requests ----------------
elif tab == "Swap Requests":
    st.header("🔄 Manage Your Swap Requests")
    user = st.text_input("Enter your name to view your requests")
    sent = swaps_df[swaps_df["from_user"] == user]
    received = swaps_df[swaps_df["to_user"] == user]

    st.subheader("📤 Sent Requests")
    for idx, row in sent.iterrows():
        st.markdown(f"To: **{row['to_user']}** | Status: *{row['status']}*")
        if row["status"] == "pending":
            if st.button("Delete Request", key=f"del{idx}"):
                swaps_df.drop(idx, inplace=True)
                swaps_df.to_csv("swap_requests.csv", index=False)
                st.success("Deleted.")

    st.subheader("📥 Received Requests")
    for idx, row in received.iterrows():
        st.markdown(f"From: **{row['from_user']}** - _{row['message']}_")
        if row["status"] == "pending":
            if st.button("Accept", key=f"acc{idx}"):
                swaps_df.at[idx, "status"] = "accepted"
            if st.button("Reject", key=f"rej{idx}"):
                swaps_df.at[idx, "status"] = "rejected"
    swaps_df.to_csv("swap_requests.csv", index=False)

# ---------------- Feedback ----------------
elif tab == "Feedback":
    st.header("🌟 Leave Feedback After Swap")
    from_user = st.text_input("Your Name")
    to_user = st.text_input("Whom You Swapped With")
    rating = st.slider("Rating", 1, 5)
    comment = st.text_area("Comment")
    if st.button("Submit Feedback"):
        new_fb = pd.DataFrame([{
            "from_user": from_user, "to_user": to_user,
            "rating": rating, "comment": comment
        }])
        feedback_df = pd.concat([feedback_df, new_fb], ignore_index=True)
        feedback_df.to_csv("feedback.csv", index=False)
        st.success("Feedback submitted!")

# ---------------- Admin Panel ----------------
elif tab == "Admin":
    st.header("🛠 Admin Dashboard")
    password = st.text_input("Enter admin password", type="password")
    if password == "admin123":
        st.success("Access granted.")
        st.subheader("📄 All Users")
        st.dataframe(users_df)
        st.subheader("🔁 Swap Requests")
        st.dataframe(swaps_df)
        st.subheader("🌟 Feedback")
        st.dataframe(feedback_df)

        st.download_button("Download User Data", users_df.to_csv(index=False), "users.csv")
        st.download_button("Download Swaps", swaps_df.to_csv(index=False), "swaps.csv")
        st.download_button("Download Feedback", feedback_df.to_csv(index=False), "feedback.csv")
    else:
        st.warning("Enter valid admin password.")
