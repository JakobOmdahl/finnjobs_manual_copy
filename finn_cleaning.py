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


def drop_na(table: pd.DataFrame, column: str):
    return table.drop(table.loc[(table[column] == "") | (table[column] == " ")].index)


skill_node = pd.DataFrame(list(skill_count.items()), columns=["Skill", "Count"])
skill_node.sort_values(by="Count", ascending=False, inplace=True)

skill_node = drop_na(skill_node, "Skill")


listing = pd.DataFrame(df[["Finn_code", "Industry"]].drop_duplicates())
listing["Industry"] = listing["Industry"].apply(lambda x: x.split(",")[0])
# listing["Industry"][14]==""


listing = drop_na(listing, "Industry")


edges_between_listing_skill = []
for index, row in df.iterrows():
    finn_code = row["Finn_code"]
    skills = row["Skills"].split(",")
    for skill in skills:
        edges_between_listing_skill.append((finn_code, skill))

edges_between_listing_skill = pd.DataFrame(
    edges_between_listing_skill, columns=["Finn_code", "Skill"]
)

edges_between_listing_skill = drop_na(edges_between_listing_skill, "Skill")
edges_between_listing_skill.drop_duplicates(inplace=True)

edges_between_listing_skill.to_csv("edges.csv", index=False, encoding="utf-8-sig")
listing.to_csv("listings.csv", index=False, encoding="utf-8-sig")
df.to_csv("rawdata.csv", index=False, encoding="utf-8-sig")
skill_node.to_csv("finn_skill_nodes.csv", index=False, encoding="utf-8-sig")
