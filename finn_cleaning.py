import json

import pandas as pd

with open("finn_jobs.txt", "r", encoding="utf-8") as file:
    lines = file.read()
text = lines.split("||")
clean_text = text[1 : len(text) - 1]
rows = [json.loads(part) for part in clean_text]


df = pd.DataFrame(rows)
df.drop_duplicates(inplace=True)

skills = []
for row in df["Skills"]:
    lst = row.split(",")
    skills.extend(lst)

cleaned_skills = set(skills)

skill_count = {}

for skill in cleaned_skills:
    count = 0
    for num in skills:
        if skill == num:
            count += 1
        else:
            continue
    skill_count[skill] = count


skill_node = pd.DataFrame(list(skill_count.items()), columns=["Skill", "Count"])
skill_node.sort_values(by="Count", ascending=False, inplace=True)

skill_node.drop(
    skill_node.loc[(skill_node["Skill"] == "") | (skill_node["Skill"] == " ")].index,
    inplace=True,
)

listing = pd.DataFrame(df[["Finn_code", "Industry"]].drop_duplicates())
listing["Industry"] = listing["Industry"].apply(lambda x: x.split(",")[0])
# listing["Industry"][14]==""


listing.drop(
    listing.loc[(listing["Industry"] == "") | (listing["Industry"] == " ")].index,
    inplace=True,
)

listing.to_csv("listings.csv", index=False, encoding="utf-8-sig")
df.to_csv("rawdata.csv", index=False, encoding="utf-8-sig")
skill_node.to_csv("finn_skill_nodes.csv", index=False, encoding="utf-8-sig")
