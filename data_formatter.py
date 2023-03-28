import os
import re

import numpy as np
import pandas as pd


class DataFormatter:
    def __init__(self, files_dir):
        self.files_dir = files_dir
        self.common_cols = []
        self.set_common_cols()

    def rename_files(self):
        pattern = r'(The_Best_)(.+)(_for|_in)'
        for root, dir_names, file_names in os.walk(self.files_dir):
            for file_name in file_names:
                new_file_name = re.findall(pattern, file_name)[0][1]
                os.rename(os.path.join(root, file_name), os.path.join(root, new_file_name))

    def add_csv_ending(self):
        for root, dir_names, file_names in os.walk(self.files_dir):
            for file_name in file_names:
                full_file_name = os.path.join(root, file_name)
                os.rename(full_file_name, f"{full_file_name}.csv")

    def delete_first_2_columns(self):
        for root, dir_names, file_names in os.walk(self.files_dir):
            for file_name in file_names:
                full_file_name = os.path.join(root, file_name)
                df = pd.read_csv(full_file_name)
                # df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                df.drop('Source Url', axis=1, inplace=True)
                df.drop('Url', axis=1, inplace=True)
                df.to_csv(full_file_name)

    def delete_first_3_rows(self):
        # "2-in-1_Laptops.csv", "Battery_Life_Laptops.csv", "Business_Laptops.csv",
        # "Laptops_for_College_Students.csv", "Laptops_for_Video_Editing.csv"
        files_to_delete_from = ["Business_Laptops.csv"]
        for root, dir_names, file_names in os.walk(self.files_dir):
            for file_name in file_names:
                if file_name not in files_to_delete_from:
                    continue
                full_file_name = os.path.join(root, file_name)
                df = pd.read_csv(full_file_name)
                df.drop(index=[0, 1, 2], inplace=True)
                df.to_csv(full_file_name)

    @staticmethod
    def get_df_with_column_names(df):
        df_col4 = df['Column 4']
        pattern = r"#(\w+):"
        new_df = pd.DataFrame()
        new_df['Name'] = []

        for item in df_col4:
            column_name = re.findall(pattern, item)
            if len(column_name) == 0:
                continue
            new_df[column_name[0]] = []

        return new_df

    def get_cols_intersection(self, df_list):
        common_cols = df_list[0].columns
        for i in range(1, len(df_list)):
            df_cols_2 = df_list[i].columns
            common_cols = common_cols.intersection(df_cols_2)

        self.common_cols = common_cols

    def set_common_cols(self):
        df_list = []
        for root, dir_names, file_names in os.walk(self.files_dir):
            for file_name in file_names:
                full_file_name = os.path.join(root, file_name)
                df = pd.read_csv(full_file_name)
                new_df = self.get_df_with_column_names(df)
                df_list.append(new_df)

        self.get_cols_intersection(df_list)

    def create_new_dfs_with_cols_from(self, full_file_name):
        df = pd.read_csv(full_file_name)
        new_df = pd.DataFrame()
        pattern = r"#\w+:(.+)"
        column_nrs = ["Column 4", "Column 5", "Column 6", "Column 7", "Column 8", "Column 9",
                      "Column 10", "Column 11", "Column 12"]

        for index, row in df.iterrows():
            column_items = []
            # it's the name!
            if "#" not in row[1]:
                for i in range(1, len(row)):
                    column_items.append(row[i])
                try:
                    new_df.insert(0, "Name", np.array(column_items))
                except ValueError:
                    pass
                continue

            for col_name in self.common_cols:
                if re.search(f"{col_name}:", row["Column 4"]):
                    for i in range(1, len(row)):
                        items = re.findall(pattern, row[i])

                        if len(items) == 0:
                            column_items.append(None)

                            continue
                        column_items.append(items[0])
                    try:
                        new_df.insert(0, col_name, np.array(column_items))
                    except ValueError:
                        pass

        return new_df

    def create_new_dfs(self):
        for root, dir_names, file_names in os.walk(self.files_dir):
            for file_name in file_names:
                full_file_name = os.path.join(root, file_name)
                new_df = self.create_new_dfs_with_cols_from(full_file_name)
                new_df.to_csv(f"new/{file_name}")


if __name__ == '__main__':
    dataFormatter = DataFormatter('resources')
    dataFormatter.create_new_dfs()
