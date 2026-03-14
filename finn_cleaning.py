import json

import pandas as pd

df = pd.DataFrame(
    columns=[
        "file",
        "Job_title",
        "Company",
        "Skills",
        "Sector",
        "Location",
        "Industry",
        "Position",
        "Keywords",
        "Finn_code",
    ]
)


def read_file(file: str, df: pd.DataFrame):
    with open(file, "r", encoding="utf-8") as input:
        lines = input.read()
        text = lines.split("||")
        file_name = text[0].rstrip()
        clean_text = text[1 : len(text) - 1]
        rows = [json.loads(part) for part in clean_text]
        for row in rows:
            row["file"] = file_name
        df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)

    return df


file_names = [
    r"data\business_analyst.txt",
    r"data\data_analyst.txt",
    r"data\big_data.txt",
    r"data\data_og_ai.txt",
    r"data\analytic_engineer.txt",
    r"data\data_science.txt",
    r"data\forretningsanalyse.txt",
    r"data\forretningsanalyse.txt",
    r"data\machine_learning.txt",
    r"data\machine_learning.txt",
   r"data\analyse.txt",
]

for file_name in file_names:
    df = read_file(file_name, df)


df.drop_duplicates(subset="Finn_code", keep="first", inplace=True)


skills = []
for row in df["Skills"]:
    lst = row.split(",")
    skills.extend(lst)

clean_skills = []
for skill in skills:
    clean_skills.append(skill.rstrip().lstrip())


cleaned_skills = set(clean_skills)

skill_count = {}

for skill in cleaned_skills:
    count = 0
    for num in clean_skills:
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
