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


def normalize_skill(skill: str) -> str:
    return " ".join(skill.replace("\xa0", " ").strip().lower().split())


file_names = [
    r"data\business_analyst.txt",
    r"data\data_analyst.txt",
    r"data\big_data.txt",
    r"data\data_og_ai.txt",
    r"data\analytic_engineer.txt",
    r"data\data_science.txt",
    r"data\forretningsanalyse.txt",
    r"data\forretningsanalytiker.txt",
    r"data\machine_learning.txt",
    # r"data\analyse.txt",
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
    clean_skills.append(normalize_skill(skill))


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
    mask = table[column].notna() & table[column].astype(str).str.strip().ne("")
    return table.loc[mask].copy()


skill_node = pd.DataFrame(list(skill_count.items()), columns=["Skill", "Count"])
skill_node.sort_values(by="Count", ascending=False, inplace=True)

skill_node = drop_na(skill_node, "Skill")
skill_node.head()

bad_skills = skill_node[skill_node["Count"] == 1]
bad_skills = set(bad_skills["Skill"])

bad_listing = set()
for index, row in df.iterrows():
    skill_list = (normalize_skill(x) for x in row["Skills"].split(","))
    if all(item in bad_skills for item in skill_list):
        bad_listing.add(row["Finn_code"])

listing = pd.DataFrame(df[["Finn_code", "Industry"]].drop_duplicates())
listing["Industry"] = listing["Industry"].apply(lambda x: x.split(",")[0])


listing = drop_na(listing, "Industry")


edges_between_listing_skill = []
for index, row in df.iterrows():
    finn_code = row["Finn_code"]
    industry = row["Industry"].split(",")[0]
    skills = row["Skills"].split(",")
    for skill in skills:
        edges_between_listing_skill.append((finn_code, skill, industry))

edges_between_listing_skill = pd.DataFrame(
    edges_between_listing_skill, columns=["Finn_code", "Skill", "Industry"]
)


edges_between_listing_skill = drop_na(edges_between_listing_skill, "Skill")
edges_between_listing_skill.drop_duplicates(inplace=True)


nodes_original_plan = pd.DataFrame(
    columns=["Id", "Label", "Node_Type", "Search_Word", "Skill_Weight"]
)

job_ad_type = "Job Ad"
skill_type = "Skill"
jobs = pd.DataFrame(columns=["Id", "Label", "Node_Type", "Search_Word", "Skill_Weight"])
jobs["Id"] = df["Finn_code"]
jobs["Label"] = ""
jobs["Node_Type"] = job_ad_type
jobs["Search_Word"] = df["file"]
jobs["Skill_Weight"] = 0

skill_list = pd.DataFrame(
    columns=["Id", "Label", "Node_Type", "Search_Word", "Skill_Weight"]
)
skill_list["Id"] = skill_node["Skill"].apply(normalize_skill)
skill_list["Label"] = skill_node["Skill"]
skill_list["Node_Type"] = skill_type
skill_list["Search_Word"] = ""
skill_list["Skill_Weight"] = skill_node["Count"]
skill_list.reset_index(drop=True, inplace=True)


nodes_original_plan = pd.concat([jobs, skill_list], ignore_index=True)

nodes_original_plan = nodes_original_plan[~nodes_original_plan.Id.isin(bad_skills)]
nodes_original_plan = nodes_original_plan[~nodes_original_plan.Id.isin(bad_listing)]

nodes_original_plan.to_csv(
    "data_nodes_original_plan.csv", index=False, encoding="utf-8-sig"
)

edges_original_plan = pd.DataFrame(columns=["Source", "Target", "Type", "Industry"])
type_ = "Undirected"

edges_original_plan["Source"] = edges_between_listing_skill["Finn_code"]
edges_original_plan["Target"] = edges_between_listing_skill["Skill"].apply(
    normalize_skill
)
edges_original_plan["Type"] = type_
edges_original_plan["Industry"] = edges_between_listing_skill["Industry"]


edges_original_plan = edges_original_plan[~edges_original_plan.Target.isin(bad_skills)]
edges_original_plan = edges_original_plan[~edges_original_plan.Source.isin(bad_listing)]

edges_original_plan.to_csv(
    "data_edges_original_plan.csv", index=False, encoding="utf-8-sig"
)

node_skill_bridging = pd.DataFrame(columns=["Id", "Label", "Skill_Count"])
node_skill_bridging["Id"] = skill_node["Skill"]
node_skill_bridging["Label"] = skill_node["Skill"]
node_skill_bridging["Skill_Count"] = skill_node["Count"]
node_skill_bridging.to_csv(
    "data_node_skill_bridging.csv", index=False, encoding="utf-8-sig"
)


skill_bridging = pd.DataFrame(columns=["Source", "Target", "Type", "Industry"])


for index, row in df.iterrows():
    input = pd.DataFrame(columns=["Source", "Target", "Type", "Industry"])
    skills = row.Skills.split(",")
    for skill1 in skills:
        for skill2 in skills:
            if skill1 != skill2:
                input["Source"] = skill1
                input["Target"] = skill2
                input["Type"] = "Undirected"
                input["Industry"] = row["Industry"]
                skill_bridging = pd.concat([skill_bridging, input], ignore_index=True)

skill_bridging.to_csv("data_edge_skill_bridging.csv", index=False, encoding="utf-8-sig")
